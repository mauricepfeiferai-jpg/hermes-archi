#!/bin/bash
# Silver Loop: Research Ingestion (dynamic)
set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
STATE="$REPO/state/libraries"
GOLD="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/GOLD_NUGGETS"
EXPORT="$HOME/.openclaw/workspace/ai-empire/04_OUTPUT/CLAUDE_EXPORT"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H-%M)
OUTFILE="$STATE/daily_ingest_${DATE}_${TIME}.json"
RESEARCH_DIR="$REPO/agents/research"

mkdir -p "$STATE" "$GOLD" "$EXPORT"

python3 - "$REPO" "$OUTFILE" "$DATE" "$TIME" "$RESEARCH_DIR" "$GOLD" "$EXPORT" <<PYTHON
import json, sys, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

repo, outfile, date, time, research_dir, gold_dir, export_dir = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5]), Path(sys.argv[6]), Path(sys.argv[7])

discovered = []

print("🔍 GitHub search...")
try:
    result = subprocess.run(["python3", str(research_dir / "github_ai_search.py")], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        data = json.loads(result.stdout.splitlines()[-1])
        discovered.append(data)
    else:
        discovered.append({"source": "github_search", "count": 0, "error": result.stderr[-200:]})
except Exception as e:
    discovered.append({"source": "github_search", "count": 0, "error": str(e)})

print("🔍 arXiv papers...")
try:
    result = subprocess.run(["python3", str(research_dir / "arxiv_ai_papers.py")], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        data = json.loads(result.stdout.splitlines()[-1])
        discovered.append(data)
    else:
        discovered.append({"source": "arxiv", "count": 0, "error": result.stderr[-200:]})
except Exception as e:
    discovered.append({"source": "arxiv", "count": 0, "error": str(e)})

print("🔍 Hacker News AI...")
try:
    result = subprocess.run(["python3", str(research_dir / "hackernews_ai.py")], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        data = json.loads(result.stdout.splitlines()[-1])
        discovered.append(data)
    else:
        discovered.append({"source": "hackernews", "count": 0, "error": result.stderr[-200:]})
except Exception as e:
    discovered.append({"source": "hackernews", "count": 0, "error": str(e)})

# Ollama Cloud fallback if GitHub gave no results
if not any(d.get("count", 0) > 0 and d.get("source") == "github_search" for d in discovered):
    print("🤖 Ollama Cloud fallback...")
    try:
        import requests
        url = "http://localhost:11434/api/generate"
        prompt = "List 10 trending open-source AI agent / LLM / MCP repos launched in the last 7 days. Return JSON array with keys: owner, repo, hint, stars, url."
        payload = {"model": "deepseek-v4-flash:cloud", "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        content = r.json().get("response", "")
        start = content.find("[")
        end = content.rfind("]")
        if start >= 0 and end > start:
            items = json.loads(content[start:end+1])
            discovered.append({"source": "ollama_cloud_fallback", "count": len(items), "items": items})
        else:
            discovered.append({"source": "ollama_cloud_fallback", "count": 0, "note": "no JSON array found"})
    except Exception as e:
        discovered.append({"source": "ollama_cloud_fallback", "count": 0, "error": str(e)})

total = sum(d.get("count", 0) for d in discovered)
result = {"date": date, "time": time, "source": "22-research-ingestion.sh", "total": total, "discovered": discovered}
outfile.parent.mkdir(parents=True, exist_ok=True)
outfile.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "library.entry",
    "source": "22-research-ingestion.sh",
    "payload": {"file": str(outfile), "items": total, "sources": [d.get("source") for d in discovered]},
    "recipients": ["emperor", "openclaw_main", "dashboard"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_library.entry.json").write_text(json.dumps(event, indent=2))
print(f"🧠 Neural bus: library.entry ({total} items)")

nugget = ("# GOLD NUGGET — Research Ingest " + date + " " + time + "\n\n" +
          "Datum: " + date + " " + time + "\n" +
          "Source: GitHub Search / arXiv / HackerNews / Ollama Cloud Fallback\n" +
          "File: " + str(outfile) + "\n\n" +
          "Zusammenfassung\n- " + str(total) + " Eintraege entdeckt\n" +
          "- Sources: " + ", ".join(d.get("source") for d in discovered) + "\n\n" +
          "Naechster Schritt\nCTO prueft Eintraege; Emperor priorisiert vielversprechende Repos.\n")
ng = gold_dir / ("GOLD_RESEARCH_INGEST_" + date + "_" + time + ".md")
ng.write_text(nugget)
(export_dir / ng.name).write_text(nugget)
print(f"✅ Research ingest complete: {outfile}")
PYTHON
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
ops/cron/22-research-ingestion.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
