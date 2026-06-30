#!/bin/bash
# Silver Loop: Research Ingestion
# Daily discovery of new AI repos, tools, papers, and signals.
# Writes to state/libraries/daily_ingest_YYYY-MM-DD.json

set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
STATE="$REPO/state/libraries"
GOLD="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/GOLD_NUGGETS"
EXPORT="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/CLAUDE_EXPORT"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H-%M)
OUTFILE="$STATE/daily_ingest_${DATE}.json"
RESEARCH_DIR="$REPO/agents/research"

mkdir -p "$STATE" "$GOLD" "$EXPORT"

cat > "$OUTFILE.tmp" <<JSON
{"date": "${DATE}", "source": "research_ingest", "discovered": []}
JSON

# --- GitHub AI repos via search API ---
echo "🔍 Fetching GitHub AI repos via search API..."
python3 "$RESEARCH_DIR/github_ai_search.py" >> "$OUTFILE.tmp" 2>/dev/null || true

# --- arXiv AI papers ---
echo "🔍 Fetching arXiv AI papers..."
python3 "$RESEARCH_DIR/arxiv_ai_papers.py" >> "$OUTFILE.tmp" 2>/dev/null || true

# --- Hacker News AI stories ---
echo "🔍 Fetching Hacker News AI stories..."
python3 "$RESEARCH_DIR/hackernews_ai.py" >> "$OUTFILE.tmp" 2>/dev/null || true

# --- Assemble final ingest file ---
python3 - "$OUTFILE.tmp" "$OUTFILE" <<PY
import json, sys
from pathlib import Path

infile, outfile = sys.argv[1], sys.argv[2]
raw = Path(infile).read_text().strip().splitlines()
entries = []
for line in raw:
    line = line.strip()
    if not line:
        continue
    try:
        entries.append(json.loads(line))
    except Exception:
        pass

header = entries[0] if entries else {}
discovered = [e for e in entries[1:] if isinstance(e, dict)]

result = {
    "date": header.get("date", "") if isinstance(header, dict) else "",
    "source": "research_ingest",
    "discovered": discovered
}
Path(outfile).write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
PY

rm -f "$OUTFILE.tmp"

# --- Emit neural bus event ---
python3 - "$REPO" <<PY
import json, sys
from pathlib import Path
from datetime import datetime, timezone

repo = Path(sys.argv[1])
outfile = repo / "state" / "libraries" / f"daily_ingest_{datetime.now().strftime('%Y-%m-%d')}.json"
content = json.loads(outfile.read_text())
items = sum(len(d.get("items", [])) for d in content.get("discovered", []))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
event = {
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "type": "library.entry",
    "source": "22-research-ingestion.sh",
    "payload": {"file": str(outfile), "items": items, "sources": [d.get("source") for d in content.get("discovered", [])]},
    "recipients": ["emperor", "openclaw_main", "dashboard"]
}
(bus_dir / f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z').replace(':', '-').replace('.', '-')}_library.entry.json").write_text(json.dumps(event, indent=2))
print(f"🧠 Neural bus event emitted: library.entry ({items} items)")
PY

# --- Gold Nugget candidate ---
cat > "$GOLD/GOLD_RESEARCH_INGEST_${DATE}.md" <<MD
# 💰 GOLD NUGGET — Research Ingest $DATE

**Datum:** $DATE
**Source:** GitHub Search + arXiv AI + Hacker News
**File:** $OUTFILE

## Kurzfassung
Tägliche Entdeckungsphase für Agent OS Library. Daten landen in \`state/libraries/\` und Neural Bus.

## Nächster Schritt
CTO Agent prüft Einträge; Emperor Agent priorisiert vielversprechende Repos für 09_LIBRARY.
MD

cp "$GOLD/GOLD_RESEARCH_INGEST_${DATE}.md" "$EXPORT/" 2>/dev/null || true

echo "✅ Research ingest complete: $OUTFILE"
