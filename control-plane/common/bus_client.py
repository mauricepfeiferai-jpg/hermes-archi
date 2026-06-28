"""Bus client — used by Jarvis / OpenClaw / Harvey to talk to Hermes."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from .models import AgentRegistration, BusMessage, MessageType

log = logging.getLogger("bus_client")


class BusClient:
    """Thin async wrapper around Hermes /dispatch."""

    def __init__(self, hermes_url: str | None = None, agent_name: str = "unknown"):
        self.hermes_url = hermes_url or os.getenv("HERMES_URL", "http://127.0.0.1:18790")
        self.agent_name = agent_name
        self._client = httpx.AsyncClient(timeout=60.0)

    async def dispatch(
        self,
        to: str | None,
        type_: MessageType,
        payload: dict[str, Any],
        intent: str | None = None,
        reply_to: str | None = None,
        trace_id: str | None = None,
    ) -> BusMessage:
        msg = BusMessage(
            **{"from": self.agent_name},
            to=to,
            type=type_,
            intent=intent,
            payload=payload,
            reply_to=reply_to,
            trace_id=trace_id,
        )
        resp = await self._client.post(
            f"{self.hermes_url}/dispatch",
            json=msg.model_dump(by_alias=True),
        )
        resp.raise_for_status()
        data = resp.json()
        return BusMessage.model_validate(data)

    async def register(self, url: str, capabilities: list[str], pid: int | None = None) -> None:
        reg = AgentRegistration(name=self.agent_name, url=url, capabilities=capabilities, pid=pid)
        try:
            await self._client.post(f"{self.hermes_url}/register", json=reg.model_dump())
            log.info("Registered with Hermes: %s @ %s", self.agent_name, url)
        except Exception as e:
            log.warning("Failed to register with Hermes: %s", e)

    async def health_ping(self) -> dict | None:
        try:
            r = await self._client.get(f"{self.hermes_url}/health")
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None

    async def close(self) -> None:
        await self._client.aclose()
