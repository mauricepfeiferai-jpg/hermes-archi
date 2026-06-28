"""OpenClaw skill registry — discovery + run.

Discovery sources:
  1. /.openclaw/openclaw.json  → skills.entries (canonical list)
  2. /openclaw/workspace/skills/*/SKILL.md (presence check)

Run-strategy:
  1. Call Ollama directly using SKILL.md as system-prompt context.
  2. Fallback: return a helpful stub if Ollama is unreachable.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
from pathlib import Path
from typing import Any

log = logging.getLogger("openclaw.skills")

OPENCLAW_CONFIG = Path(os.getenv(
    "OPENCLAW_CONFIG",
    Path(__file__).resolve().parents[3] / ".openclaw" / "openclaw.json",
))
WORKSPACE = Path(os.getenv(
    "OPENCLAW_WORKSPACE",
    Path(__file__).resolve().parents[3] / "openclaw" / "workspace" / "skills",
))


INTENT_TO_SKILL: dict[str, str] = {
    "content_creation": "content-engine",
    "code_generation": "pi-coder",
    "youtube_publish": "youtube-factory",
    "browser_action": "x-twitter-browser",
    "seo_audit": "seo-ranker",
    "trading_monitor": "trading-monitor",
    "meta_ads": "meta-ads",
}


class SkillRegistry:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.by_name: dict[str, dict[str, Any]] = {}

    def discover(self) -> None:
        # 1. Canonical list from openclaw.json
        if OPENCLAW_CONFIG.exists():
            try:
                cfg = json.loads(OPENCLAW_CONFIG.read_text())
                for name, spec in cfg.get("skills", {}).get("entries", {}).items():
                    enabled = spec.get("enabled", True)
                    if enabled:
                        self.entries.append({
                            "name": name,
                            "source": "config",
                            "skill_md": str(WORKSPACE / name / "SKILL.md"),
                        })
            except Exception as e:
                log.warning("Failed to parse openclaw.json: %s", e)

        # 2. Workspace discovery (might find extras not in config)
        if WORKSPACE.exists():
            for skill_md in WORKSPACE.glob("*/SKILL.md"):
                name = skill_md.parent.name
                if name in self.by_name_set():
                    continue
                self.entries.append({
                    "name": name,
                    "source": "workspace",
                    "skill_md": str(skill_md),
                })

        self.by_name = {e["name"]: e for e in self.entries}

    def by_name_set(self) -> set[str]:
        return {e["name"] for e in self.entries}

    def capabilities(self) -> list[str]:
        caps = ["browser", "skills", "file"]
        names = self.by_name_set()
        if any(n in names for n in ("content-engine", "x-twitter-browser")):
            caps.append("content_creation")
        if "pi-coder" in names:
            caps.append("code_generation")
        if any(n in names for n in ("youtube-factory", "youtube-studio-uploader")):
            caps.append("youtube_publish")
        if "trading-monitor" in names:
            caps.append("trading_monitor")
        if "seo-ranker" in names:
            caps.append("seo")
        if "meta-ads" in names:
            caps.append("meta_ads")
        return caps

    def match_intent(self, intent: str | None) -> str | None:
        if not intent:
            return None
        skill = INTENT_TO_SKILL.get(intent)
        if skill and skill in self.by_name:
            return skill
        return None

    def get(self, name: str) -> dict[str, Any] | None:
        return self.by_name.get(name)

    def _load_skill_md(self, name: str) -> str:
        skill = self.get(name)
        if not skill:
            return ""
        path = Path(skill.get("skill_md", ""))
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are the {name} skill. Execute the user's request."

    def _call_ollama(self, system: str, user: str) -> str | None:
        ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        model = os.getenv("OPENCLAW_MODEL", "qwen3:14b")
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{ollama_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
            return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            log.warning("Ollama call failed for skill %s: %s", model, e)
            return None

    async def run(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        skill = self.get(name)
        if not skill:
            return {"status": "unknown", "stub": True,
                    "reply": f"Skill {name} not registered."}

        text_in = payload.get("text", payload.get("message", ""))
        system_prompt = self._load_skill_md(name)

        reply = self._call_ollama(system_prompt, text_in)
        if reply:
            return {
                "status": "done",
                "stub": False,
                "skill": name,
                "reply": reply,
                "artifacts": [],
            }

        # Ollama unreachable — informative fallback
        return {
            "status": "ollama_unavailable",
            "stub": True,
            "skill": name,
            "reply": (
                f"[OpenClaw] Skill `{name}` bereit, aber Ollama nicht erreichbar. "
                f"Starte Ollama und versuche es erneut."
            ),
            "artifacts": [],
        }
