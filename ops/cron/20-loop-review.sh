#!/bin/bash
# Silver Loop: Daily Review
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
mkdir -p "$REPO/loop"
python3 - "$REPO" "$DATE" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, date = Path(sys.argv[1]), sys.argv[2]

bus_dir = repo / "state" / "neural-bus"
cutoff = datetime.now(timezone.utc).timestamp() - 24 * 3600
events = []
for f in sorted(bus_dir.glob("*.json")):
    try:
        ev = json.loads(f.read_text())
        ts = datetime.fromisoformat(ev.get("ts", "").replace("Z", "+00:00"))
        if ts.timestamp() > cutoff:
            events.append(ev)
    except Exception:
        pass

lessons_file = repo / "loop" / "lessons.json"
lessons = json.loads(lessons_file.read_text()) if lessons_file.exists() else []

library_count = sum(1 for e in events if "library" in e.get("type", ""))
dopamine_events = [e for e in events if "dopamine" in e.get("type", "")]
if library_count >= 1:
    lessons.append({"date": date, "lesson": "Daily research ingest works — keep 08:00 slot", "confidence": "high"})
if dopamine_events:
    last = dopamine_events[-1].get("payload", {})
    if last.get("score", 0) < 5:
        lessons.append({"date": date, "lesson": "Dopamine score low — ship something visible today", "confidence": "high"})

lessons = lessons[-50:]
lessons_file.write_text(json.dumps(lessons, indent=2))

bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "loop.review.completed",
    "source": "20-loop-review.sh",
    "payload": {"events_24h": len(events), "lessons": len(lessons), "new_lessons": len([l for l in lessons if l.get("date") == date])},
    "recipients": ["emperor", "loop_agent"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_loop.review.completed.json").write_text(json.dumps(event, indent=2))
print(f"Loop review: {len(events)} events, {len(lessons)} lessons")
PYTHON
