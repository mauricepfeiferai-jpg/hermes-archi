#!/bin/bash
# Silver Loop: Writer Content
# L1 report-only. Surfaces work for human approval.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUT="$REPO/state/10/10-writer-content_$DATE.json"
mkdir -p "$(dirname "$OUT")"
python3 - "$REPO" "$OUT" "$DATE" "$TIME" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, outfile, date, time = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]

report = {
    "date": date,
    "time": time,
    "source": "10-writer-content.sh",
    "role": "Writer Content",
    "action": "Draft content from product queue",
    "status": "L1_report_only",
    "items": [],
    "note": "Human approval required before any external action."
}
outfile.parent.mkdir(parents=True, exist_ok=True)
outfile.write_text(json.dumps(report, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "agent.10-writer-content.ready",
    "source": "10-writer-content.sh",
    "payload": report,
    "recipients": ["emperor", "10"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_agent.10-writer-content.ready.json").write_text(json.dumps(event, indent=2))
print(f"Writer Content: {outfile}")
PYTHON
