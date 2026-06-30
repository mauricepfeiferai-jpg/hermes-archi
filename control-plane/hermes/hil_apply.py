#!/usr/bin/env python3
"""Apply HIL gate check to any existing cron script without modifying it."""
import json, subprocess, sys
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
        "source": "hil_apply.py",
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
    if len(sys.argv) < 3:
        print("Usage: hil_apply.py <loop-name> <action-desc> -- <command...>")
        sys.exit(1)

    loop_name = sys.argv[1]
    action_desc = sys.argv[2]
    sep_idx = sys.argv.index("--")
    command = sys.argv[sep_idx + 1:]

    gate = classify(action_desc)
    emit("hil.apply.gate_check", {
        "loop": loop_name,
        "action": action_desc,
        "gate": gate["gate"],
        "reason": gate["reason"]
    })

    print(f"[HIL] {loop_name}: {gate['gate']} — {gate['reason']}")

    if gate["gate"] == "RED":
        emit("hil.apply.red.blocked", {"loop": loop_name, "reason": gate["reason"]})
        print(f"[HIL] ⛔ RED gate blocked {loop_name}. Human decision required.")
        return 77

    if gate["gate"] == "YELLOW":
        emit("hil.apply.yellow.prepared", {"loop": loop_name})
        print(f"[HIL] 🟡 YELLOW gate: {loop_name} prepared, human approval required before execution")
        # For L1/L2 cron loops, yellow still executes but logs the gate
        # Future: create Decision Card and exit instead

    print(f"[HIL] 🟢 Running {loop_name}: {' '.join(command)}")
    result = subprocess.run(command)
    status = "success" if result.returncode == 0 else "failure"
    emit(f"hil.apply.{gate['gate'].lower()}.{status}", {
        "loop": loop_name,
        "exit_code": result.returncode,
        "gate_reason": gate["reason"]
    })
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
