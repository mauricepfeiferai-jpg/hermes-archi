#!/bin/bash
# Silver Loop: Dopamine Scoring
# Reads yesterday's neural bus events, scores completed work, updates dopamine state.

set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

python3 - "$REPO" "$YESTERDAY" "$DATE" <<PY
import json, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

repo, yesterday, today = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
bus_dir = repo / "state" / "neural-bus"
dopamine_dir = repo / "state" / "dopamine"
dopamine_dir.mkdir(parents=True, exist_ok=True)

score_file = dopamine_dir / "score.json"
history_file = dopamine_dir / "history.json"

score_state = {"score": 0.0, "streak": 0, "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
if score_file.exists():
    score_state = json.loads(score_file.read_text())

# Decay (biochemical forgetting curve)
score_state["score"] *= 0.95

# Collect yesterday's events
events = []
for f in bus_dir.glob("*.json"):
    try:
        ev = json.loads(f.read_text())
        if yesterday in ev.get("ts", ""):
            events.append(ev)
    except Exception:
        pass

# Compute deltas
delta = 0.0
breakdown = []
for ev in events:
    etype = ev.get("type", "")
    payload = ev.get("payload", {})
    if etype == "code.completed":
        d = payload.get("files", 0) * 0.1 + payload.get("tests_passed", 0) * 2 + payload.get("commits", 0) * 1 + payload.get("merged_prs", 0) * 5
    elif etype == "skill.created":
        d = 10
    elif etype == "library.entry":
        d = 3
    elif etype == "library.sync.completed":
        d = 1
    elif etype == "agent.task.completed":
        d = 1
    elif etype == "revenue":
        d = payload.get("amount", 0) * 50
    else:
        d = 0.1
    delta += d
    breakdown.append({"type": etype, "delta": round(d, 2), "source": ev.get("source", "")})

score_state["score"] = round(score_state["score"] + delta, 2)
score_state["last_delta"] = round(delta, 2)
score_state["last_event"] = "dopamine.daily_score"
score_state["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

if delta >= 5:
    score_state["streak"] = score_state.get("streak", 0) + 1
else:
    score_state["streak"] = 0

score_file.write_text(json.dumps(score_state, indent=2))

history = []
if history_file.exists():
    history = json.loads(history_file.read_text())
history.append({
    "ts": score_state["last_updated"],
    "date": today,
    "delta": round(delta, 2),
    "score": score_state["score"],
    "streak": score_state["streak"],
    "breakdown": breakdown,
})
history_file.write_text(json.dumps(history[-365:], indent=2))

# Reward signal on neural bus
bus_dir.mkdir(parents=True, exist_ok=True)
event = {
    "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "type": "dopamine.score.updated",
    "source": "24-dopamine-score.sh",
    "payload": score_state,
    "recipients": ["emperor", "openclaw_main", "dashboard", "loop_agent"]
}
(bus_dir / f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z').replace(':', '-').replace('.', '-')}_dopamine.score.updated.json").write_text(json.dumps(event, indent=2))

print(f"🧠 Dopamine score: {score_state['score']} (+{round(delta, 2)}), streak: {score_state['streak']}")
PY

echo "✅ Dopamine score updated"
