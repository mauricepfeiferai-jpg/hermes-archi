#!/usr/bin/env python3
"""Human-in-the-Loop wrapper for any command or action.
Runs gate classification and enforces GREEN/YELLOW/RED execution policy.
"""
import json, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"


def classify(action_text: str) -> dict:
    classifier = REPO / "control-plane" / "hermes" / "gate_classifier.py"
    result = subprocess.run(
        [sys.executable, str(classifier), action_text],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout)


def emit_neural_event(event_type: str, payload: dict):
    bus_dir = REPO / "state" / "neural-bus"
    bus_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    event = {
        "ts": now.isoformat().replace("+00:00", "Z"),
        "type": event_type,
        "source": "hil_wrapper.py",
        "payload": payload,
        "recipients": ["emperor"]
    }
    ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
    (bus_dir / f"{ts}_{event_type}.json").write_text(json.dumps(event, indent=2))


def main():
    if len(sys.argv) < 3:
        print("Usage: hil_wrapper.py <action-description> -- <command...>")
        print("  or:  hil_wrapper.py <action-description> --auto-approve -- <command...>")
        sys.exit(1)

    action_desc = sys.argv[1]
    auto_approve = "--auto-approve" in sys.argv
    if auto_approve:
        sys.argv.remove("--auto-approve")

    sep_idx = sys.argv.index("--")
    command = sys.argv[sep_idx + 1:]

    gate = classify(action_desc)
    print(f"HIL Gate: {gate['gate']} — {gate['reason']}")

    if gate["gate"] == "RED":
        print("⛔ RED gate — human decision required. Aborting execution.")
        emit_neural_event("hil.red.blocked", {"action": action_desc, "reason": gate["reason"]})
        sys.exit(77)

    if gate["gate"] == "YELLOW" and not auto_approve:
        print("🟡 YELLOW gate — human approval required.")
        print(f"Proposed action: {action_desc}")
        print(f"Command: {' '.join(command)}")
        response = input("Approve? (yes/no): ").strip().lower()
        if response not in ("yes", "y", "ja", "j"):
            print("Aborted by user.")
            emit_neural_event("hil.yellow.denied", {"action": action_desc})
            sys.exit(78)

    print(f"🟢 Executing: {' '.join(command)}")
    result = subprocess.run(command)

    status = "success" if result.returncode == 0 else "failure"
    emit_neural_event(f"hil.{gate['gate'].lower()}.{status}", {
        "action": action_desc,
        "command": command,
        "exit_code": result.returncode,
        "gate_reason": gate["reason"]
    })
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
