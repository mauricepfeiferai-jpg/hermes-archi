"""Harvey runtime — Legal & Sales Counsel.

Port: 18792 (default)

Bridges to existing TypeScript code under /integrations/telegram/src/:
  - legal_review.ts (PDF/DOCX extraction + LLM legal analysis)
  - stripe_webhook.ts (incoming payments)

For Phase 2 MVP, this Python adapter handles:
  - bus /handle endpoint (Hermes-routed)
  - direct LLM call via Ollama (deepseek-r1:32b) for legal_review intent
  - stripe webhook proxy (HMAC verify + KG-audit)
  - usage tracking in /var/lib/harvey/legal_usage (own dir; legacy .openclaw stays read-only)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, Request

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common import BusClient, BusMessage, HealthResponse, MessageType  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal import LegalReviewer  # noqa: E402
from stripe_bridge import StripeBridge  # noqa: E402

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [harvey] %(message)s",
)
log = logging.getLogger("harvey")

app = FastAPI(title="Harvey — Legal & Sales", version="1.0.0")

START_TIME = time.time()
PORT = int(os.getenv("HARVEY_PORT", "18792"))
SELF_URL = os.getenv("HARVEY_URL", f"http://127.0.0.1:{PORT}")
HERMES_URL = os.getenv("HERMES_URL", "http://127.0.0.1:18790")

bus = BusClient(hermes_url=HERMES_URL, agent_name="harvey")
reviewer = LegalReviewer()
stripe = StripeBridge()


@app.on_event("startup")
async def _startup() -> None:
    log.info("Harvey starting on %s", SELF_URL)
    await asyncio.sleep(0.5)
    await bus.register(
        url=SELF_URL,
        capabilities=["legal", "legal_review", "stripe", "trading_decision",
                      "sales", "compliance", "payment_event"],
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
        name="harvey",
        capabilities=["legal_review", "stripe", "sales", "trading_signal"],
    )


@app.post("/handle")
async def handle(msg: BusMessage) -> dict:
    """Bus entry."""
    log.info("BUS ← from=%s intent=%s", msg.from_, msg.intent)

    intent = msg.intent or ""

    if intent in ("legal_review", "settlement", "evidence_matrix"):
        return await reviewer.handle(msg.payload, intent)

    if intent in ("sales_pipeline", "customer_email", "revenue_audit"):
        return {
            "reply": (
                f"[Harvey] Intent `{intent}` registriert. "
                f"Sales-Skills sind in Phase 3 verkabelt — hier nur Stub."
            ),
            "stub": True,
        }

    if intent == "trading_decision":
        return {
            "reply": (
                "[Harvey] Trading-Signal-Modus: NUR Signale, kein Live-Execute. "
                "Risiko-Bewertung folgt in Phase 3."
            ),
            "stub": True,
            "safety_gate": "signal_only",
        }

    if intent == "stripe_event":
        # Should usually arrive via /webhooks/stripe, but route via bus is allowed
        return await stripe.handle_event(msg.payload)

    return {
        "reply": f"[Harvey] Intent `{intent}` nicht erkannt.",
        "status": "unknown_intent",
    }


@app.post("/webhooks/stripe")
async def stripe_webhook(req: Request, stripe_signature: str = Header(default="")) -> dict:
    """Receive Stripe webhook directly. HMAC-verified."""
    body = await req.body()
    try:
        event = stripe.verify_and_parse(body, stripe_signature)
    except ValueError as e:
        raise HTTPException(400, f"signature invalid: {e}") from e
    log.info("Stripe event: %s", event.get("type"))
    return await stripe.handle_event(event)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORT)
