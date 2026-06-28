"""Hermes Router — capability-based dispatch to downstream agents."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.models import (  # noqa: E402
    AgentHealth,
    AgentRegistration,
    BusMessage,
    MessageType,
)

log = logging.getLogger("hermes.router")

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class RoutingError(Exception):
    pass


class Router:
    def __init__(self) -> None:
        self.agents: dict[str, dict] = {}
        self.stats: dict[str, dict] = {}
        self._client: httpx.AsyncClient | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._start_time = time.time()
        self._load_config()

    def _load_config(self) -> None:
        if not CONFIG_PATH.exists():
            log.warning("Hermes config not found at %s — starting empty", CONFIG_PATH)
            return
        with CONFIG_PATH.open() as f:
            cfg = json.load(f)
        for name, spec in cfg.get("agents", {}).items():
            self.agents[name] = {
                "name": name,
                "url": spec["url"],
                "capabilities": spec.get("capabilities", []),
                "priority": spec.get("priority", 5),
                "status": "unknown",
                "last_heartbeat": None,
            }
            self.stats[name] = {"routed": 0, "errors": 0}
        self.intent_routing: dict[str, str] = cfg.get("intent_routing", {})
        self.fallback_order: list[str] = cfg.get("fallback_order", list(self.agents.keys()))
        self.timeout = cfg.get("limits", {}).get("messageTimeoutSec", 60)

    async def start(self) -> None:
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def close(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._client:
            await self._client.aclose()

    def register(self, reg: AgentRegistration) -> None:
        existing = self.agents.get(reg.name, {})
        self.agents[reg.name] = {
            **existing,
            "name": reg.name,
            "url": reg.url,
            "capabilities": reg.capabilities,
            "status": "healthy",
            "last_heartbeat": time.time(),
        }
        self.stats.setdefault(reg.name, {"routed": 0, "errors": 0})

    def agents_health(self) -> list[AgentHealth]:
        return [
            AgentHealth(
                name=a["name"],
                status=a["status"],
                last_heartbeat=(
                    None if a["last_heartbeat"] is None
                    else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(a["last_heartbeat"]))
                ),
                capabilities=a["capabilities"],
                url=a["url"],
            )
            for a in self.agents.values()
        ]

    def agent_health(self, name: str) -> AgentHealth | None:
        a = self.agents.get(name)
        if not a:
            return None
        return AgentHealth(
            name=a["name"], status=a["status"], capabilities=a["capabilities"], url=a["url"],
            last_heartbeat=(None if a["last_heartbeat"] is None
                            else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(a["last_heartbeat"]))),
        )

    # ------------------------------------------------------------------
    #  Routing
    # ------------------------------------------------------------------

    def pick_agent(self, msg: BusMessage) -> str:
        """Pick the best agent based on (1) explicit `to` (2) intent → capability."""
        if msg.to and msg.to in self.agents:
            return msg.to
        if msg.intent:
            cap = self.intent_routing.get(msg.intent)
            if cap:
                for name, agent in self.agents.items():
                    if cap in agent["capabilities"] and agent["status"] != "down":
                        return name
        for name in self.fallback_order:
            if name in self.agents and self.agents[name]["status"] != "down":
                return name
        raise RoutingError(f"No agent available for msg {msg.id} (to={msg.to}, intent={msg.intent})")

    async def deliver(self, msg: BusMessage) -> BusMessage | None:
        target = self.pick_agent(msg)
        agent = self.agents[target]
        url = agent["url"].rstrip("/") + "/handle"
        self.stats[target]["routed"] += 1
        log.info("→ %s (%s)", target, url)
        try:
            resp = await self._client.post(url, json=msg.model_dump(by_alias=True))
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            # Agents return plain dicts; wrap into a proper response BusMessage
            if isinstance(data, dict) and "from" not in data:
                return BusMessage(
                    **{"from": target}, to=msg.from_,
                    type=MessageType.RESULT,
                    intent=msg.intent,
                    payload=data,
                    reply_to=msg.id,
                    trace_id=msg.trace_id or msg.id,
                )
            return BusMessage.model_validate(data)
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            self.stats[target]["errors"] += 1
            agent["status"] = "degraded"
            log.warning("Delivery to %s failed: %s", target, e)
            raise RoutingError(f"Delivery failed: {target}: {e}") from e

    # ------------------------------------------------------------------
    #  Heartbeat-loop
    # ------------------------------------------------------------------

    async def _heartbeat_loop(self) -> None:
        while True:
            await asyncio.sleep(30)
            await self._ping_all()

    async def _ping_all(self) -> None:
        for name, agent in self.agents.items():
            url = agent["url"].rstrip("/") + "/health"
            try:
                r = await self._client.get(url, timeout=5)
                if r.status_code == 200:
                    agent["status"] = "healthy"
                    agent["last_heartbeat"] = time.time()
                else:
                    agent["status"] = "degraded"
            except Exception:
                if agent["status"] == "healthy":
                    log.warning("Agent %s unreachable", name)
                agent["status"] = "down"
