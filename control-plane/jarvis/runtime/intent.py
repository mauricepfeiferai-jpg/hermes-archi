"""Jarvis Intent Router — loads router.yaml and matches user text."""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

log = logging.getLogger("jarvis.intent")

ROUTER_PATH = Path(__file__).resolve().parents[1] / "router.yaml"


@dataclass
class Intent:
    id: str
    handler: str = "self"
    delegate_to: str | None = None
    skill_hint: str | None = None
    needs_confirmation: bool = False
    goal_template: str | None = None
    raw: dict[str, Any] | None = None


class IntentRouter:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or ROUTER_PATH
        self.intents: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            log.warning("Router YAML not found at %s", self.path)
            return
        with self.path.open() as f:
            data = yaml.safe_load(f) or {}
        self.intents = data.get("intents", [])
        log.info("Loaded %d intents from %s", len(self.intents), self.path)

    def classify(self, text: str) -> Intent:
        lower = text.lower()
        for spec in self.intents:
            triggers = spec.get("triggers", [])
            for t in triggers:
                t_low = t.lower()
                if t_low in lower or re.search(rf"\b{re.escape(t_low)}\b", lower):
                    return Intent(
                        id=spec["id"],
                        handler=spec.get("handler", "delegate"),
                        delegate_to=spec.get("delegate_to"),
                        skill_hint=spec.get("skill_hint"),
                        needs_confirmation=spec.get("needs_confirmation", False),
                        goal_template=spec.get("goal_template"),
                        raw=spec,
                    )
        # default: self-handle as conversation
        return Intent(id="fallback_conversation", handler="self")
