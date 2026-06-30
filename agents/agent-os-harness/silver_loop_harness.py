#!/usr/bin/env python3
"""
Silver Loop Harness
Fixed, fast reflex loops. No reasoning in the hot path.
Reads state/neural-bus/ events and triggers registered silver loops.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
LOOPS_DIR = REPO / "templates" / "agent-os-silver-loops"
BUS_DIR = REPO / "state" / "neural-bus"
STATE_DIR = REPO / "state" / "silver-loops"

LOOPS = [
    {
        "id": "silver_morning_queue",
        "trigger": "cron.06:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "06-ceo-daily-goals.sh")],
        "enabled": True,
    },
    {
        "id": "silver_tech_health",
        "trigger": "cron.06:15",
        "action": ["bash", str(REPO / "ops" / "cron" / "07-cto-tech-health.sh")],
        "enabled": True,
    },
    {
        "id": "silver_ship",
        "trigger": "cron.07:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "08-engineer-ship.sh")],
        "enabled": True,
    },
    {
        "id": "silver_research_ingest",
        "trigger": "cron.08:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "22-research-ingestion.sh")],
        "enabled": True,
    },
    {
        "id": "silver_library_sync",
        "trigger": "cron.08:30",
        "action": ["bash", str(REPO / "ops" / "cron" / "23-library-sync.sh")],
        "enabled": True,
    },
    {
        "id": "silver_dopamine_score",
        "trigger": "cron.09:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "24-dopamine-score.sh")],
        "enabled": True,
    },
    {
        "id": "silver_neural_broadcast",
        "trigger": "cron.09:15",
        "action": ["bash", str(REPO / "ops" / "cron" / "25-neural-broadcast.sh")],
        "enabled": True,
    },
    {
        "id": "silver_backup_health",
        "trigger": "cron.18:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "19-ops-backup-health.sh")],
        "enabled": True,
    },
    {
        "id": "silver_daily_review",
        "trigger": "cron.20:00",
        "action": ["bash", str(REPO / "ops" / "cron" / "20-loop-review.sh")],
        "enabled": True,
    },
    {
        "id": "silver_self_improve",
        "trigger": "cron.20:30",
        "action": ["bash", str(REPO / "ops" / "cron" / "21-loop-improve.sh")],
        "enabled": True,
    },
    {
        "id": "silver_code_completed_dopamine",
        "trigger": "event.code.completed",
        "action": ["python3", str(REPO / "agents" / "agent-os-harness" / "dispatch.py"), "emperor", "score dopamine for completed code"],
        "enabled": True,
    },
    {
        "id": "silver_library_added_neural_broadcast",
        "trigger": "event.library.entry",
        "action": ["python3", str(REPO / "agents" / "agent-os-harness" / "dispatch.py"), "openclaw_main", "notify: new library entry"],
        "enabled": True,
    },
]


def load_events():
    events = []
    if not BUS_DIR.exists():
        return events
    for f in sorted(BUS_DIR.glob("*.json")):
        try:
            with open(f) as fh:
                events.append(json.load(fh))
        except Exception:
            pass
    return events


def run_action(loop, event=None):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    log = {
        "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "loop_id": loop["id"],
        "trigger": loop["trigger"],
        "event": event,
        "action": loop["action"],
    }
    try:
        result = subprocess.run(
            loop["action"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO,
        )
        log["rc"] = result.returncode
        log["stdout"] = result.stdout[-1000:]
        log["stderr"] = result.stderr[-500:]
    except Exception as e:
        log["error"] = str(e)

    log_file = STATE_DIR / f"{loop['id']}_{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z').replace(':', '-').replace('.', '-')}.json"
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)
    return log


def run_all(trigger_filter=None):
    results = []
    for loop in LOOPS:
        if not loop.get("enabled", True):
            continue
        if trigger_filter and not loop["trigger"].startswith(trigger_filter):
            continue
        results.append(run_action(loop))
    return results


def react_to_events():
    events = load_events()
    results = []
    for event in events:
        etype = event.get("type", "")
        for loop in LOOPS:
            if not loop.get("enabled", True):
                continue
            if loop["trigger"] == f"event.{etype}":
                results.append(run_action(loop, event))
    return results


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "run"
    if command == "list":
        print(json.dumps(LOOPS, indent=2))
    elif command == "run":
        trigger = sys.argv[2] if len(sys.argv) > 2 else None
        results = run_all(trigger)
        print(json.dumps(results, indent=2))
    elif command == "react":
        results = react_to_events()
        print(json.dumps(results, indent=2))
    else:
        print("Usage: silver_loop_harness.py [list|run [trigger_prefix]|react]")


if __name__ == "__main__":
    main()
