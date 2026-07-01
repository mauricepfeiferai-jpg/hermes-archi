#!/bin/bash
# Silver Loop: Self-Improvement
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
cd "$REPO"
source .venv/bin/activate
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
mkdir -p "$REPO/state/loop"
python3 - "$REPO" "$DATE" <<PYTHON
import json, sys
from pathlib import Path
from datetime import datetime, timezone
repo, date = Path(sys.argv[1]), sys.argv[2]

lessons_file = repo / "loop" / "lessons.json"
lessons = json.loads(lessons_file.read_text()) if lessons_file.exists() else []

suggestions = []
for lesson in lessons[-10:]:
    txt = lesson.get("lesson", "").lower()
    if "research" in txt:
        suggestions.append({"target": "22-research-ingestion.sh", "action": "consider adding new source", "reason": lesson["lesson"]})
    if "dopamine" in txt:
        suggestions.append({"target": "24-dopamine-score.sh", "action": "review scoring weights", "reason": lesson["lesson"]})
    if "ship" in txt:
        suggestions.append({"target": "08-engineer-ship.sh", "action": "lower human-gate threshold", "reason": lesson["lesson"]})

improvement = {
    "date": date,
    "source": "21-loop-improve.sh",
    "lessons_reviewed": len(lessons),
    "suggestions": suggestions,
    "note": "L1 report-only. Human approves before applying patches.",
}
(repo / "state" / "loop" / f"improvement_{date}.json").write_text(json.dumps(improvement, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "loop.improvement.suggested",
    "source": "21-loop-improve.sh",
    "payload": improvement,
    "recipients": ["emperor", "loop_agent"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_loop.improvement.suggested.json").write_text(json.dumps(event, indent=2))
print(f"Loop improvement: {len(suggestions)} suggestions")
PYTHON
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
21-loop-improve.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
