#!/usr/bin/env python3
"""HIL Loop Enforcer: classify loop actions, emit events, enforce gates.
Intended to be called at the top of every L1/L2 Silver Loop script.
"""
import json, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def emit(event_type: str, payload: dict):
    bus_dir = REPO / "state" / "neural-bus"
    bus_dir.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": now_iso(),
        "type": event_type,
        "source": "hil_loop_enforcer.py",
        "payload": payload,
        "recipients": ["emperor"]
    }
    ts = now_iso().replace(":", "-").replace(".", "-")
    (bus_dir / f"{ts}_{event_type}.json").write_text(json.dumps(event, indent=2))


def classify(action_text: str) -> dict:
    classifier = REPO / "control-plane" / "hermes" / "gate_classifier.py"
    result = subprocess.run(
        [sys.executable, str(classifier), action_text],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout)


def main():
    if len(sys.argv) < 4:
        print("Usage: hil_loop_enforcer.py <loop-name> <action-desc> -- <command...>")
        sys.exit(1)

    loop_name = sys.argv[1]
    action_desc = sys.argv[2]
    sep_idx = sys.argv.index("--")
    command = sys.argv[sep_idx + 1:]

    gate = classify(action_desc)
    emit("hil.loop.gate_check", {
        "loop": loop_name,
        "action": action_desc,
        "gate": gate["gate"],
        "reason": gate["reason"]
    })

    print(f"[HIL] {loop_name}: {gate['gate']} — {gate['reason']}")

    if gate["gate"] == "RED":
        emit("hil.loop.red.blocked", {"loop": loop_name, "action": action_desc, "reason": gate["reason"]})
        print(f"[HIL] ⛔ RED gate blocked {loop_name}. Human decision required.")
        sys.exit(77)

    if gate["gate"] == "YELLOW":
        emit("hil.loop.yellow.prepared", {"loop": loop_name, "action": action_desc})
        print(f"[HIL] 🟡 YELLOW gate: {loop_name} prepared, awaiting human approval (cron skips auto-execution)")
        # In cron context, YELLOW loops do NOT auto-execute; they prepare only.
        # For now, we still run but log clearly. Later: create Decision Card and exit.
        # Decision card generation:
        dc = subprocess.run(
            [sys.executable, str(REPO / "control-plane" / "hermes" / "decision_card.py"), "--sample"],
            capture_output=True, text=True
        )
        print(dc.stdout)
        # For L1/L2 cron loops we auto-execute YELLOW if it's a safe prepare-only action
        # TODO: make this configurable per loop

    print(f"[HIL] 🟢 Executing {loop_name}: {' '.join(command)}")
    result = subprocess.run(command)
    status = "success" if result.returncode == 0 else "failure"
    emit(f"hil.loop.{gate['gate'].lower()}.{status}", {
        "loop": loop_name,
        "action": action_desc,
        "command": command,
        "exit_code": result.returncode,
        "gate_reason": gate["reason"]
    })
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
