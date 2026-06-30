#!/bin/bash
# Silver Loop: Researcher Scan
# L1 report-only. Surfaces work for human approval.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUT="$REPO/state/09/09-researcher-scan_$DATE.json"
mkdir -p "$(dirname "$OUT")"
python3 - "$REPO" "$OUT" "$DATE" "$TIME" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, outfile, date, time = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]

report = {
    "date": date,
    "time": time,
    "source": "09-researcher-scan.sh",
    "role": "Researcher Scan",
    "action": "Scan GitHub/HN/arXiv for AI signals",
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
    "type": "agent.09-researcher-scan.ready",
    "source": "09-researcher-scan.sh",
    "payload": report,
    "recipients": ["emperor", "09"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_agent.09-researcher-scan.ready.json").write_text(json.dumps(event, indent=2))
print(f"Researcher Scan: {outfile}")
PYTHON
