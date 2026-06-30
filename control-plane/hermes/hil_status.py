#!/usr/bin/env python3
"""Generate HIL status report from neural-bus events."""
import json
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
BUS_DIR = REPO / "state" / "neural-bus"
OUT = REPO / "state" / "hil" / "status.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def load_events():
    events = []
    if not BUS_DIR.exists():
        return events
    for f in BUS_DIR.glob("*.json"):
        try:
            e = json.loads(f.read_text())
            events.append(e)
        except Exception:
            continue
    return events


def main():
    events = load_events()
    hil_events = [e for e in events if e.get("type", "").startswith("hil.")]

    gate_checks = [e for e in hil_events if e["type"] == "hil.apply.gate_check"]
    red_blocks = [e for e in hil_events if "red.blocked" in e["type"]]
    yellow_prep = [e for e in hil_events if "yellow.prepared" in e["type"]]
    green_exec = [e for e in hil_events if "green.success" in e["type"]]
    failures = [e for e in hil_events if e["type"].endswith(".failure")]

    loop_stats = {}
    for e in gate_checks:
        loop = e.get("payload", {}).get("loop", "unknown")
        gate = e.get("payload", {}).get("gate", "UNKNOWN")
        if loop not in loop_stats:
            loop_stats[loop] = {"GREEN": 0, "YELLOW": 0, "RED": 0, "last": e.get("ts")}
        loop_stats[loop][gate] = loop_stats[loop].get(gate, 0) + 1
        if e.get("ts") > loop_stats[loop]["last"]:
            loop_stats[loop]["last"] = e.get("ts")

    status = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_gate_checks": len(gate_checks),
        "red_blocks": len(red_blocks),
        "yellow_preparations": len(yellow_prep),
        "green_executions": len(green_exec),
        "failures": len(failures),
        "loops": loop_stats,
        "last_red_block": red_blocks[-1].get("ts") if red_blocks else None,
        "last_yellow": yellow_prep[-1].get("ts") if yellow_prep else None,
    }
    OUT.write_text(json.dumps(status, indent=2))
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
