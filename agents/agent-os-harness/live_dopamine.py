#!/usr/bin/env python3
"""Emit a live dopamine reward for a completed task."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
DOPAMINE_DIR = REPO / "state" / "dopamine"
BUS_DIR = REPO / "state" / "neural-bus"


def score_event(event_type, payload):
    if event_type == "code.completed":
        return round(
            payload.get("files", 0) * 0.1 +
            payload.get("tests_passed", 0) * 2 +
            payload.get("commits", 0) * 1 +
            payload.get("merged_prs", 0) * 5,
            2
        )
    elif event_type == "skill.created":
        return 10
    elif event_type == "library.entry":
        return 3
    elif event_type == "revenue":
        return payload.get("amount", 0) * 50
    return 1


def emit_and_score(event_type, payload):
    DOPAMINE_DIR.mkdir(parents=True, exist_ok=True)
    BUS_DIR.mkdir(parents=True, exist_ok=True)

    score_file = DOPAMINE_DIR / "score.json"
    state = {"score": 0.0, "streak": 0}
    if score_file.exists():
        state = json.loads(score_file.read_text())

    delta = score_event(event_type, payload)
    state["score"] = round(state.get("score", 0.0) + delta, 2)
    state["last_delta"] = delta
    state["last_event"] = event_type
    state["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    score_file.write_text(json.dumps(state, indent=2))

    event = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "type": event_type,
        "source": "live_dopamine.py",
        "payload": {**payload, "dopamine_delta": delta},
        "recipients": ["emperor", "openclaw_main", "dashboard"],
    }
    fname = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-") + f"_{event_type}.json"
    (BUS_DIR / fname).write_text(json.dumps(event, indent=2))

    print(f"🧠 Dopamine +{delta}: {event_type}")
    print(f"   Total score: {state['score']}")
    return state


if __name__ == "__main__":
    event_type = sys.argv[1] if len(sys.argv) > 1 else "code.completed"
    payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    emit_and_score(event_type, payload)
