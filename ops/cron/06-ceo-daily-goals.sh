#!/bin/bash
# Silver Loop: CEO Morning Queue
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
MEMORY="$HOME/.openclaw/workspace/ai-empire/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUT="$REPO/state/ceo/morning_queue_${DATE}.json"
mkdir -p "$REPO/state/ceo"
python3 - "$REPO" "$MEMORY" "$OUT" "$DATE" "$TIME" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, memory_dir, outfile, date, time = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], sys.argv[5]

current = memory_dir / "CURRENT.md"
decisions = memory_dir / "DECISIONS.md"
next_file = memory_dir / "NEXT.md"
mem_text = ""
for f in [current, decisions, next_file]:
    if f.exists():
        mem_text += f"\n\n## {f.name}\n" + f.read_text()

dopamine = {"score": 0, "streak": 0}
dop_file = repo / "state" / "dopamine" / "score.json"
if dop_file.exists():
    dopamine = json.loads(dop_file.read_text())

queue = {
    "date": date,
    "time": time,
    "source": "06-ceo-daily-goals.sh",
    "dopamine": dopamine,
    "priorities": [
        {"rank": 1, "action": "Post launch content (X/LinkedIn)", "owner": "writer", "blocked_by": "manual_approval", "impact": "revenue"},
        {"rank": 2, "action": "Watch PayPal / deliver ZIP on sale", "owner": "sales", "blocked_by": "sale_event", "impact": "revenue"},
        {"rank": 3, "action": "Research ingest + library sync", "owner": "researcher", "blocked_by": "none", "impact": "knowledge"},
        {"rank": 4, "action": "Loop audit + score improvement", "owner": "loop_agent", "blocked_by": "none", "impact": "system"},
    ],
    "memory_snapshot": mem_text[:2000],
}
outfile.parent.mkdir(parents=True, exist_ok=True)
outfile.write_text(json.dumps(queue, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "ceo.morning_queue",
    "source": "06-ceo-daily-goals.sh",
    "payload": {"queue_file": str(outfile), "priorities": len(queue["priorities"])},
    "recipients": ["emperor", "writer", "sales", "researcher", "loop_agent", "openclaw_main"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_ceo.morning_queue.json").write_text(json.dumps(event, indent=2))
print(f"CEO morning queue: {outfile}")
PYTHON
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
ops/cron/06-ceo-daily-goals.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
