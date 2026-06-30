#!/bin/bash
# Silver Loop: Research Ingestion
# Daily discovery of new AI repos, tools, papers, and signals.
# Writes to state/libraries/daily_ingest_YYYY-MM-DD.json
# Also creates Gold Nugget candidates in 04_OUTPUT/GOLD_NUGGETS/

set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
STATE="$REPO/state/libraries"
GOLD="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/GOLD_NUGGETS"
EXPORT="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/CLAUDE_EXPORT"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H-%M)
OUTFILE="$STATE/daily_ingest_${DATE}.json"

mkdir -p "$STATE" "$GOLD" "$EXPORT"

cat > "$OUTFILE.tmp" <<JSON
{
  "date": "$DATE",
  "source": "research_ingest",
  "discovered": []
}
JSON

# --- GitHub trending AI repos (read-only, no auth required) ---
echo "🔍 Scraping GitHub trending..."
python3 - <<PY >> "$OUTFILE.tmp" 2>/dev/null || true
import json, urllib.request, sys, datetime
from html.parser import HTMLParser

class RepoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.repos = []
        self.current_href = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href", "").startswith("/") and attrs.get("href", "").count("/") == 2:
            parts = attrs["href"].strip("/").split("/")
            if len(parts) == 2 and "." not in parts[0]:
                self.current_href = attrs["href"]
    def handle_data(self, data):
        if self.current_href and data.strip() and len(data.strip()) < 80:
            self.repos.append({"owner": self.current_href.split("/")[1], "repo": self.current_href.split("/")[2], "hint": data.strip()})
            self.current_href = None

try:
    url = "https://github.com/trending?since=daily"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    parser = RepoParser()
    parser.feed(html)
    # Filter AI-related
    ai_keywords = ["ai", "agent", "llm", "gpt", "claude", "automation", "mcp", "prompt", "workflow", "code", "model"]
    ai_repos = [r for r in parser.repos[:50] if any(k in (r["hint"] + r["repo"]).lower() for k in ai_keywords)]
    result = {"source": "github_trending", "count": len(ai_repos), "items": ai_repos[:10]}
    print(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({"source": "github_trending", "count": 0, "error": str(e)}))
PY

# --- arXiv AI papers (simple RSS feed) ---
echo "🔍 Fetching arXiv AI papers..."
python3 - <<PY >> "$OUTFILE.tmp" 2>/dev/null || true
import json, urllib.request, xml.etree.ElementTree as ET
try:
    url = "http://export.arxiv.org/rss/cs.AI"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    root = ET.fromstring(data)
    papers = []
    for item in root.iter("item"):
        title = item.find("title")
        link = item.find("link")
        if title is not None and link is not None:
            papers.append({"title": title.text.strip(), "link": link.text.strip()})
    print(json.dumps({"source": "arxiv_ai", "count": len(papers), "items": papers[:5]}))
except Exception as e:
    print(json.dumps({"source": "arxiv_ai", "count": 0, "error": str(e)}))
PY

# --- Hacker News AI stories ---
echo "🔍 Fetching Hacker News..."
python3 - <<PY >> "$OUTFILE.tmp" 2>/dev/null || true
import json, urllib.request
try:
    top = json.loads(urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).read())
    stories = []
    for sid in top[:30]:
        story = json.loads(urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10).read())
        if story and any(k in (story.get("title", "") + story.get("text", "")).lower() for k in ["ai", "llm", "agent", "claude", "gpt", "model"]):
            stories.append({"title": story.get("title"), "url": story.get("url"), "score": story.get("score")})
    print(json.dumps({"source": "hackernews_ai", "count": len(stories), "items": stories[:5]}))
except Exception as e:
    print(json.dumps({"source": "hackernews_ai", "count": 0, "error": str(e)}))
PY

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

result = {
    "date": entries[0]["date"] if entries else "",
    "source": "research_ingest",
    "discovered": [e for e in entries[1:] if isinstance(e, dict)]
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
    "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
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
**Source:** GitHub Trending + arXiv AI + Hacker News
**File:** $OUTFILE

## Kurzfassung
Tägliche Entdeckungsphase für Agent OS Library. Daten landen in \`state/libraries/\` und Neural Bus.

## Nächster Schritt
CTO Agent prüft Einträge; Emperor Agent priorisiert vielversprechende Repos für 09_LIBRARY.
MD

cp "$GOLD/GOLD_RESEARCH_INGEST_${DATE}.md" "$EXPORT/" 2>/dev/null || true

echo "✅ Research ingest complete: $OUTFILE"
