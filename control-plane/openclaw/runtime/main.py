"""OpenClaw runtime — Execution Engine adapter.

Port: 18789 (default — same as existing OpenClaw Gateway, can be overridden)

This is a thin Python adapter that:
  - exposes /handle for Hermes bus messages
  - discovers skills from /.openclaw/openclaw.json
  - delegates skill execution to:
      a) existing /openclaw/ Node gateway (if running, via HTTP)
      b) a local sub-process for Python skills
      c) a stub-handler returning "skill not yet wired"

For Phase 2 MVP: option (c) is the default for unknown skills;
options (a)+(b) are wiring placeholders for Phase 3.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common import BusClient, BusMessage, HealthResponse, MessageType  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skills import SkillRegistry  # noqa: E402

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [openclaw] %(message)s",
)
log = logging.getLogger("openclaw")

app = FastAPI(title="OpenClaw — Execution Engine", version="1.0.0")

START_TIME = time.time()
PORT = int(os.getenv("OPENCLAW_PORT", "18789"))
SELF_URL = os.getenv("OPENCLAW_URL", f"http://127.0.0.1:{PORT}")
HERMES_URL = os.getenv("HERMES_URL", "http://127.0.0.1:18790")

skills = SkillRegistry()
bus = BusClient(hermes_url=HERMES_URL, agent_name="openclaw")


@app.on_event("startup")
async def _startup() -> None:
    log.info("OpenClaw adapter on %s", SELF_URL)
    skills.discover()
    log.info("Discovered %d skills", len(skills.entries))
    await asyncio.sleep(0.5)
    await bus.register(
        url=SELF_URL,
        capabilities=skills.capabilities(),
        pid=os.getpid(),
    )


@app.on_event("shutdown")
async def _shutdown() -> None:
    await bus.close()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=int(time.time() - START_TIME),
        name="openclaw",
        capabilities=skills.capabilities(),
    )


@app.get("/skills")
async def list_skills() -> dict:
    return {"skills": skills.entries}


@app.post("/handle")
async def handle(msg: BusMessage) -> dict:
    log.info("BUS ← from=%s intent=%s skill_hint=%s",
             msg.from_, msg.intent, msg.payload.get("skill") or msg.payload.get("skill_hint"))

    skill_name = (msg.payload.get("skill") or msg.payload.get("skill_hint")
                  or skills.match_intent(msg.intent))
    if not skill_name:
        return {
            "reply": f"OpenClaw — kein Skill für intent '{msg.intent}' gefunden.",
            "status": "skipped",
        }

    skill = skills.get(skill_name)
    if not skill:
        return {
            "reply": f"OpenClaw — Skill '{skill_name}' nicht registriert.",
            "status": "unknown_skill",
        }

    log.info("Running skill: %s", skill_name)
    result = await skills.run(skill_name, msg.payload)

    return {
        "reply": result.get("reply", f"Skill {skill_name} fertig."),
        "skill": skill_name,
        "artifacts": result.get("artifacts", []),
        "status": result.get("status", "done"),
        "stub": result.get("stub", False),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORT)
