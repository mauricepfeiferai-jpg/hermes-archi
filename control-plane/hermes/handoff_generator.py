#!/usr/bin/env python3
"""Automated handoff generator for Hermes/Hecate sessions.
Run at session end to produce HANDOFF.md + memory updates.
"""
import json, sys, os, re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
WORKSPACE = Path.home() / ".openclaw" / "workspace" / "ai-empire"
HANDOFF_PATH = REPO / "00_SYSTEM" / "HANDOFF.md"
MEMORY_DIR = WORKSPACE / "memory"
NEURAL_DIR = REPO / "state" / "neural-bus"


def find_latest_events(limit: int = 20) -> list:
    events = []
    if NEURAL_DIR.exists():
        for f in sorted(NEURAL_DIR.glob("*.json"), reverse=True)[:limit]:
            try:
                events.append(json.loads(f.read_text()))
            except Exception:
                pass
    return events


def extract_completed(events: list) -> list:
    done = []
    for e in events:
        t = e.get("type", "")
        if "completed" in t or "success" in t or "discovered" in t:
            payload = e.get("payload", {})
            action = payload.get("action", payload.get("task", t))
            done.append(action)
    return list(dict.fromkeys(done))[:10]


def extract_decisions(events: list) -> list:
    decs = []
    for e in events:
        t = e.get("type", "")
        if t.startswith("hil.") and ("blocked" in t or "denied" in t):
            payload = e.get("payload", {})
            decs.append(f"{payload.get('action', t)} — {payload.get('reason', 'human gate')}")
    return decs[:5]


def read_current_goals() -> list:
    next_file = MEMORY_DIR / "NEXT.md"
    if not next_file.exists():
        return []
    text = next_file.read_text()
    goals = []
    for line in text.splitlines():
        if re.match(r"^\d+\.\s+", line.strip()):
            goals.append(line.strip())
    return goals[:7]


def generate_handoff(completed: list, decisions: list, goals: list, extra: str = "") -> str:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        f"# HANDOFF — {now}",
        "",
        "## Gemacht",
    ]
    for item in completed:
        lines.append(f"- {item}")
    if not completed:
        lines.append("- Session aktiv, keine abschließbaren Events gefunden")

    lines.extend(["", "## Entscheidungen / Blocker"])
    for d in decisions:
        lines.append(f"- {d}")
    if not decisions:
        lines.append("- Keine YELLOW/RED-Entscheidungen in dieser Session")

    lines.extend(["", "## Nächster Schritt"])
    for g in goals:
        lines.append(f"- {g}")
    if not goals:
        lines.append("- Nächste Schritte aus NEXT.md ergänzen")

    if extra:
        lines.extend(["", "## Notizen"])
        lines.append(extra)

    lines.extend(["", "## Blocker", "- Keine"])
    return "\n".join(lines)


def update_memory():
    current_file = MEMORY_DIR / "CURRENT.md"
    stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    line = f"\n## {stamp} — Session-Handoff generiert\n\n- HANDOFF.md aktualisiert\n- Neural-Bus Events gescannt\n"
    if current_file.exists():
        current_file.write_text(current_file.read_text() + line)


def main():
    extra = ""
    if not sys.stdin.isatty():
        extra = sys.stdin.read().strip()

    events = find_latest_events(50)
    completed = extract_completed(events)
    decisions = extract_decisions(events)
    goals = read_current_goals()

    handoff = generate_handoff(completed, decisions, goals, extra)
    HANDOFF_PATH.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_PATH.write_text(handoff)
    update_memory()
    print(f"Updated handoff: {HANDOFF_PATH}")


if __name__ == "__main__":
    main()
