"""Hermes runtime — Message Bus + Goal Engine + Verifier.

Port: 18790 (default)
Endpoints:
  POST /dispatch         dispatch a message into the bus
  POST /register         agent registration
  GET  /health           service health
  GET  /agents           list registered agents
  GET  /agents/{name}    one agent's details
  POST /goals            create a goal
  GET  /goals            list goals (filter by status)
  GET  /goals/{id}       one goal
  PATCH /goals/{id}      update goal status
  POST /verify/{id}      trigger verifier run
  GET  /trace/{id}       full trace of a message-id or trace-id
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

import pydantic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# allow `python -m control-plane.hermes.runtime.main`
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.models import (  # noqa: E402
    AgentRegistration,
    BusMessage,
    GoalCard,
    GoalStatus,
    HealthResponse,
    MessageType,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import goals as goals_mod  # noqa: E402
import kg as kg_mod  # noqa: E402
import router as router_mod  # noqa: E402
import verifier as verifier_mod  # noqa: E402
from skill_writer import SkillWriter  # noqa: E402

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [hermes] %(message)s",
)
log = logging.getLogger("hermes")

app = FastAPI(title="Hermes — Pfeifer Core4 Bus", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

START_TIME = time.time()
PORT = int(os.getenv("HERMES_PORT", "18790"))

router = router_mod.Router()
kg = kg_mod.KGClient()
goal_store = goals_mod.GoalStore()
verifier = verifier_mod.Verifier(kg=kg)
skill_writer = SkillWriter()


@app.on_event("startup")
async def _startup() -> None:
    log.info("Hermes starting on port %s", PORT)
    await router.start()
    await kg.connect()
    log.info("Hermes ready. Registered agents from config: %s", list(router.agents.keys()))


@app.on_event("shutdown")
async def _shutdown() -> None:
    await router.close()
    await kg.close()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=int(time.time() - START_TIME),
        name="hermes",
        capabilities=["routing", "goal_engine", "verifier", "kg_audit"],
    )


@app.post("/dispatch")
async def dispatch(msg: BusMessage) -> BusMessage:
    """Entry point for any inter-agent communication."""
    log.info("Dispatch: %s → %s (type=%s, intent=%s)", msg.from_, msg.to, msg.type, msg.intent)

    # 1. Audit
    await kg.write_message_event(msg)

    # 2. Health pings short-circuit
    if msg.type == MessageType.HEALTH:
        return BusMessage(
            **{"from": "hermes"}, to=msg.from_, type=MessageType.HEALTH,
            payload={"status": "ok"}, reply_to=msg.id, trace_id=msg.trace_id or msg.id,
        )

    # 3. Route
    try:
        result = await router.deliver(msg)
        if result is None:
            return BusMessage(
                **{"from": "hermes"}, to=msg.from_, type=MessageType.RESULT,
                payload={"accepted": True, "note": "fire-and-forget"},
                reply_to=msg.id, trace_id=msg.trace_id or msg.id,
            )
        return result
    except router_mod.RoutingError as e:
        log.warning("Routing failed: %s", e)
        return BusMessage(
            **{"from": "hermes"}, to=msg.from_, type=MessageType.ERROR,
            payload={"error": str(e), "original_msg_id": msg.id},
            reply_to=msg.id, trace_id=msg.trace_id or msg.id,
        )


@app.post("/register")
async def register(reg: AgentRegistration) -> dict:
    router.register(reg)
    log.info("Agent registered: %s @ %s (caps=%s)", reg.name, reg.url, reg.capabilities)
    return {"ok": True, "name": reg.name}


@app.get("/agents")
async def list_agents() -> dict:
    return {"agents": [a.model_dump() for a in router.agents_health()]}


@app.get("/agents/{name}")
async def get_agent(name: str) -> dict:
    health_info = router.agent_health(name)
    if not health_info:
        raise HTTPException(404, f"agent '{name}' not found")
    return health_info.model_dump()


# ---------- Goals ----------

@app.post("/goals")
async def create_goal(goal: GoalCard) -> GoalCard:
    goal_store.save(goal)
    await kg.write_goal_event(goal, "created")
    log.info("Goal created: %s (%s) owner=%s", goal.id, goal.title, goal.owner_agent)
    # Auto-dispatch to owner
    asyncio.create_task(_kick_goal(goal))
    return goal


async def _kick_goal(goal: GoalCard) -> None:
    msg = BusMessage(
        **{"from": "hermes"}, to=goal.owner_agent, type=MessageType.TASK,
        intent=goal.context.get("intent", "execute_goal"),
        payload={"goal_id": goal.id, "goal": goal.model_dump()},
        trace_id=goal.id,
    )
    try:
        await router.deliver(msg)
    except Exception as e:
        log.warning("Kick-off for goal %s failed: %s", goal.id, e)


@app.get("/goals")
async def list_goals(status: GoalStatus | None = None) -> dict:
    return {"goals": [g.model_dump() for g in goal_store.list(status=status)]}


@app.get("/goals/{goal_id}")
async def get_goal(goal_id: str) -> GoalCard:
    g = goal_store.get(goal_id)
    if not g:
        raise HTTPException(404, f"goal '{goal_id}' not found")
    return g


@app.patch("/goals/{goal_id}")
async def update_goal(goal_id: str, patch: dict) -> GoalCard:
    g = goal_store.get(goal_id)
    if not g:
        raise HTTPException(404, f"goal '{goal_id}' not found")
    for k, v in patch.items():
        if hasattr(g, k):
            setattr(g, k, v)
    goal_store.save(g)
    await kg.write_goal_event(g, "updated")
    if g.status == GoalStatus.REVIEW:
        asyncio.create_task(_run_verifier(g))
    return g


async def _run_verifier(g: GoalCard) -> None:
    log.info("Running verifier for goal %s", g.id)
    run = await verifier.run(g)
    if run.overall == "pass":
        g.status = GoalStatus.DONE
    else:
        g.status = GoalStatus.REVIEW  # stays in review
    goal_store.save(g)


@app.post("/verify/{goal_id}")
async def verify_goal(goal_id: str) -> dict:
    g = goal_store.get(goal_id)
    if not g:
        raise HTTPException(404)
    run = await verifier.run(g)
    return run.model_dump()


@app.get("/trace/{trace_id}")
async def trace(trace_id: str) -> dict:
    return await kg.get_trace(trace_id)


# ── Self-improvement loop ────────────────────────────────────────────────────

class LearnRequest(pydantic.BaseModel):
    skill: str
    lesson: str
    agent: str = "unknown"


@app.post("/learn")
async def learn(req: LearnRequest) -> dict:
    """Any Core4 agent can POST a lesson here to improve a skill for future runs."""
    return skill_writer.write_lesson(req.skill, req.lesson, req.agent)


@app.get("/skills")
async def list_skills() -> dict:
    return {"skills": skill_writer.list_skills()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORT)
