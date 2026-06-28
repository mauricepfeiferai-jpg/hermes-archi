"""Jarvis runtime — Personal Orchestrator.

Port: 18791 (default)
Endpoints:
  GET  /health           service health
  POST /handle           receive bus message from Hermes
  POST /chat             user-facing endpoint (CLI, Telegram-Bridge)
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common import (  # noqa: E402
    BusClient,
    BusMessage,
    GoalCard,
    HealthResponse,
    MessageType,
)
from common.ollama import OllamaClient  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from intent import IntentRouter  # noqa: E402
from memory import MemoryClient  # noqa: E402

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [jarvis] %(message)s",
)
log = logging.getLogger("jarvis")

app = FastAPI(title="Jarvis — Personal Orchestrator", version="1.0.0")

START_TIME = time.time()
PORT = int(os.getenv("JARVIS_PORT", "18791"))
SELF_URL = os.getenv("JARVIS_URL", f"http://127.0.0.1:{PORT}")
HERMES_URL = os.getenv("HERMES_URL", "http://127.0.0.1:18790")

intent_router = IntentRouter()
memory = MemoryClient()
ollama = OllamaClient()
bus = BusClient(hermes_url=HERMES_URL, agent_name="jarvis")

MODEL = os.getenv("JARVIS_MODEL", "qwen3:32b")
SYSTEM_PROMPT = (
    "Du bist Jarvis, Maurice Pfeifers persönlicher AI-Orchestrator. "
    "Du sprichst Deutsch, direkt, ohne Floskeln. Du fasst dich kurz. "
    "Du delegierst Aktionen an OpenClaw (Execution) oder Harvey (Legal/Sales) "
    "via Hermes. Du redest NICHT lange — du verstehst was Maurice will und "
    "agierst. Bei Unklarheit fragst du EINE präzise Rückfrage. "
    "Ende jeder Antwort: 1 Next-Action oder 1 Frage."
)


@app.on_event("startup")
async def _startup() -> None:
    log.info("Jarvis starting on %s", SELF_URL)
    await asyncio.sleep(0.5)  # let Hermes come up
    await bus.register(
        url=SELF_URL,
        capabilities=["memory", "orchestration", "conversation", "intent_classification"],
        pid=os.getpid(),
    )
    log.info("Jarvis ready.")


@app.on_event("shutdown")
async def _shutdown() -> None:
    await bus.close()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=int(time.time() - START_TIME),
        name="jarvis",
        capabilities=["memory", "orchestration", "conversation"],
    )


@app.post("/handle")
async def handle_bus_message(msg: BusMessage) -> dict:
    """Receive a bus message routed to Jarvis by Hermes."""
    log.info("BUS ← from=%s type=%s intent=%s", msg.from_, msg.type, msg.intent)

    if msg.type == MessageType.RESULT:
        # someone (openclaw/harvey) replied to a previous task — synthesize back
        return {"ok": True, "ack": True}

    if msg.type == MessageType.TASK:
        # task targeted at jarvis itself (e.g., "memory_recall")
        return await _handle_task(msg)

    return {"ok": True}


@app.post("/chat")
async def chat(req: dict) -> dict:
    """User-facing chat endpoint. `text` and optional `user_id`."""
    text = req.get("text", "").strip()
    user_id = req.get("user_id", "maurice")
    topic_id = req.get("topic_id", 1)
    if not text:
        return {"reply": "Sag mir was an steht.", "next": "Was steht heute an?"}

    log.info("CHAT (user=%s): %s", user_id, text[:100])

    # 1. Memory recall
    ctx = await memory.recall(text, user_id=user_id)

    # 2. Intent classification
    intent = intent_router.classify(text)
    log.info("Intent: %s (delegate=%s)", intent.id, intent.delegate_to)

    # 3. Self-handled intents
    if intent.handler == "self":
        reply = await _self_reply(text, intent, ctx)
        await memory.write_turn(user_id, text, reply, intent.id)
        return {"reply": reply, "intent": intent.id, "trace": []}

    # 4. Delegate via Hermes
    payload = {
        "text": text,
        "user_id": user_id,
        "topic_id": topic_id,
        "context": ctx[:2000],
        "skill_hint": intent.skill_hint,
        "needs_confirmation": intent.needs_confirmation,
    }
    try:
        result = await bus.dispatch(
            to=intent.delegate_to,
            type_=MessageType.TASK,
            intent=intent.id,
            payload=payload,
        )
        reply_text = _extract_reply(result, intent)
    except Exception as e:
        log.warning("Bus dispatch failed: %s", e)
        reply_text = f"Konnte nicht delegieren ({intent.delegate_to} nicht erreichbar): {e}"

    await memory.write_turn(user_id, text, reply_text, intent.id)
    return {"reply": reply_text, "intent": intent.id, "delegated_to": intent.delegate_to}


async def _handle_task(msg: BusMessage) -> dict:
    intent = msg.intent or "unknown"
    if intent == "memory_recall":
        q = msg.payload.get("query", "")
        hits = await memory.search(q, limit=5)
        return {"hits": hits}
    return {"ok": True, "note": "no handler for intent " + intent}


async def _self_reply(text: str, intent, ctx: str) -> str:
    """LLM-backed answer for Jarvis-handled intents."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if ctx:
        messages.append({"role": "system", "content": f"# Relevanter Kontext\n{ctx}"})
    messages.append({"role": "user", "content": text})
    try:
        return await ollama.chat(MODEL, messages, temperature=0.5)
    except Exception as e:
        log.warning("Ollama call failed: %s", e)
        return f"(Ollama nicht erreichbar — Stub-Antwort) Du sagtest: {text[:80]}"


def _extract_reply(result: BusMessage, intent) -> str:
    if result is None:
        return f"Delegiert an {intent.delegate_to}. Antwort steht aus."
    p = result.payload or {}
    if "reply" in p:
        return str(p["reply"])
    if "summary" in p:
        return str(p["summary"])
    if "artifacts" in p:
        arts = p["artifacts"]
        if isinstance(arts, list) and arts:
            files = [a.get("path", "?") for a in arts if isinstance(a, dict)]
            return f"Fertig. Output: {', '.join(files[:5])}"
    return f"Delegiert an {intent.delegate_to}: {str(p)[:200]}"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORT)
