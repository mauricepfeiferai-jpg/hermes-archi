#!/bin/bash
# Silver Loop: Neural Broadcast
# Pushes recent neural bus events to connected systems (OpenClaw, dashboard, memory).

set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
STATE="$REPO/state"
DATE=$(date +%Y-%m-%d)

python3 - "$REPO" <<PY
import json, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

repo = Path(sys.argv[1])
bus_dir = repo / "state" / "neural-bus"
memory_dir = Path.home() / ".openclaw" / "workspace" / "ai-empire" / "memory"

# Read last 24h of events
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

# Build dashboard data
score_file = repo / "state" / "dopamine" / "score.json"
score = json.loads(score_file.read_text()) if score_file.exists() else {"score": 0}

broadcast = {
    "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "events_24h": len(events),
    "latest_event_types": [e.get("type") for e in events[-10:]],
    "dopamine_score": score.get("score", 0),
    "dopamine_streak": score.get("streak", 0),
    "recipients": ["openclaw", "hermes", "dashboard", "memory"],
}

# Regenerate dashboard data from authoritative state
dash_dir = repo / "templates" / "one-person-ai-agent-company" / "dashboard"
dash_data = dash_dir / "data.json"
if (dash_dir / "generate_data.py").exists():
    try:
        result = subprocess.run(
            ["python3", str(dash_dir / "generate_data.py")],
            capture_output=True, text=True, timeout=60, cwd=repo
        )
        print("📊 Dashboard data regenerated")
        if result.returncode != 0:
            print(result.stderr[-500:])
    except Exception as e:
        print(f"⚠️ Dashboard regenerate failed: {e}")
elif dash_data.exists():
    existing = json.loads(dash_data.read_text())
    existing["agent_os"] = broadcast
    dash_data.write_text(json.dumps(existing, indent=2))
    print("📊 Dashboard data updated (fallback)")

# Write to memory
memory_dir.mkdir(parents=True, exist_ok=True)
memory_file = memory_dir / "CURRENT.md"
if memory_file.exists():
    text = memory_file.read_text()
    lines = text.splitlines()
    lines.append(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} — Neural Broadcast")
    lines.append(f"- Events 24h: {broadcast['events_24h']}")
    lines.append(f"- Dopamine score: {broadcast['dopamine_score']}")
    lines.append(f"- Streak: {broadcast['dopamine_streak']}")
    lines.append(f"- Latest: {', '.join(broadcast['latest_event_types'])}")
    memory_file.write_text("\n".join(lines))
    print("📝 Memory updated")

# Neural bus confirmation event
confirm = {
    "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "type": "neural.broadcast.completed",
    "source": "25-neural-broadcast.sh",
    "payload": broadcast,
    "recipients": ["emperor", "openclaw_main"],
}
(bus_dir / f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z').replace(':', '-').replace('.', '-')}_neural.broadcast.completed.json").write_text(json.dumps(confirm, indent=2))
print("🧠 Neural broadcast completed")
PY

echo "✅ Neural broadcast complete"
