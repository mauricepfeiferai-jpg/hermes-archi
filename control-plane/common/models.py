"""Shared Pydantic models for the Pfeifer Core4 bus protocol.

See /control-plane/hermes/BUS.md for the canonical spec.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


class MessageType(str, Enum):
    TASK = "task"
    RESULT = "result"
    EVENT = "event"
    QUERY = "query"
    HEALTH = "health"
    BROADCAST = "broadcast"
    ERROR = "error"


class AgentName(str, Enum):
    JARVIS = "jarvis"
    HERMES = "hermes"
    OPENCLAW = "openclaw"
    HARVEY = "harvey"
    USER = "user"
    TELEGRAM = "telegram"


class BusMessage(BaseModel):
    """Canonical envelope for inter-agent communication."""

    id: str = Field(default_factory=lambda: _id("msg"))
    ts: str = Field(default_factory=_now)
    from_: str = Field(alias="from")
    to: str | None = None
    type: MessageType
    intent: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    reply_to: str | None = None
    trace_id: str | None = None
    priority: int = 5

    model_config = {"populate_by_name": True}


class AgentHealth(BaseModel):
    name: str
    status: str = "unknown"
    last_heartbeat: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    uptime_seconds: int = 0
    url: str | None = None


class AgentRegistration(BaseModel):
    name: str
    url: str
    capabilities: list[str]
    pid: int | None = None


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: int
    name: str
    version: str = "1.0.0"
    capabilities: list[str] = Field(default_factory=list)


class GoalStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class GoalCard(BaseModel):
    id: str = Field(default_factory=lambda: _id("goal"))
    title: str
    created_by: str = "jarvis"
    created_at: str = Field(default_factory=_now)
    priority: str = "P2"
    owner_agent: str
    status: GoalStatus = GoalStatus.TODO
    context: dict[str, Any] = Field(default_factory=dict)
    acceptance_criteria: list[str] = Field(default_factory=list)
    verifier: dict[str, Any] = Field(default_factory=dict)
    deadline: str | None = None
    budget: dict[str, Any] = Field(default_factory=lambda: {"spend_eur_max": 0, "human_confirmation_required": True})
    sub_goals: list[str] = Field(default_factory=list)
    notes: str | None = None
    audit: dict[str, Any] = Field(default_factory=dict)


class VerifierCheck(BaseModel):
    kind: str
    args: dict[str, Any] = Field(default_factory=dict)


class VerifierResult(BaseModel):
    check: VerifierCheck
    result: str  # pass | fail | inconclusive
    details: str = ""
    duration_ms: int = 0


class VerifierRun(BaseModel):
    goal_id: str
    run_id: str = Field(default_factory=lambda: _id("vrun"))
    ts: str = Field(default_factory=_now)
    overall: str = "pending"  # pass | fail | partial | pending
    checks: list[VerifierResult] = Field(default_factory=list)
