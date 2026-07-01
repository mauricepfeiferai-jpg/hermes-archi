#!/bin/bash
# Silver Loop: Engineer Ship
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
OUT="$REPO/state/engineer/ship_${DATE}.json"
mkdir -p "$REPO/state/engineer"
python3 - "$REPO" "$OUT" "$DATE" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, outfile, date = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]

queue_file = repo / "state" / "ceo" / f"morning_queue_{date}.json"
queue = {"priorities": []}
if queue_file.exists():
    queue = json.loads(queue_file.read_text())

ship_candidates = [p for p in queue.get("priorities", []) if p.get("blocked_by") == "none"]
shipped = []
for c in ship_candidates[:1]:
    shipped.append({**c, "status": "ready_for_human", "auto_run": False})

result = {
    "date": date,
    "source": "08-engineer-ship.sh",
    "ship_candidates": shipped,
    "blocked": [p for p in queue.get("priorities", []) if p.get("blocked_by") != "none"],
}
outfile.parent.mkdir(parents=True, exist_ok=True)
outfile.write_text(json.dumps(result, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "engineer.ship.ready",
    "source": "08-engineer-ship.sh",
    "payload": result,
    "recipients": ["emperor", "engineer", "cto"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_engineer.ship.ready.json").write_text(json.dumps(event, indent=2))
print(f"Engineer ship ready: {len(shipped)} candidates")
PYTHON
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
ops/cron/08-engineer-ship.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
