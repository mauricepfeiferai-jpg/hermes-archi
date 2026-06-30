#!/usr/bin/env python3
import json, sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"

def score_repo(item):
    score = 0
    text = (item.get("repo", "") + " " + item.get("hint", "")).lower()
    keywords = {
        "agent": 5, "mcp": 5, "llm": 4, "claude": 4, "automation": 4,
        "workflow": 4, "loop": 5, "orchestration": 4, "self-improving": 5,
        "coding": 3, "youtube": 2, "twitter": 2, "linkedin": 2, "sales": 3,
        "openclaw": 5, "hermes": 4, "skill": 3
    }
    for kw, weight in keywords.items():
        if kw in text:
            score += weight
    stars = int(item.get("stars", 0) or 0)
    score += min(stars / 1000, 10)  # cap at 10
    return round(score, 2)

def main(ingest_file=None):
    if ingest_file is None:
        files = sorted((REPO / "state" / "libraries").glob("daily_ingest_*.json"))
        if not files:
            print(json.dumps({"error": "no ingest files"}))
            return
        ingest_file = files[-1]
    else:
        ingest_file = Path(ingest_file)

    data = json.loads(ingest_file.read_text())
    all_items = []
    for source in data.get("discovered", []):
        for item in source.get("items", []):
            item["source"] = source.get("source", "unknown")
            item["ai_empire_score"] = score_repo(item)
            all_items.append(item)

    all_items.sort(key=lambda x: x["ai_empire_score"], reverse=True)

    ranked = {
        "ingest_file": str(ingest_file),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total": len(all_items),
        "top_10": all_items[:10],
        "top_score": all_items[0]["ai_empire_score"] if all_items else 0
    }

    out = REPO / "state" / "libraries" / "ranked_repos.json"
    out.write_text(json.dumps(ranked, indent=2))

    bus_dir = REPO / "state" / "neural-bus"
    bus_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    event = {
        "ts": now.isoformat().replace("+00:00", "Z"),
        "type": "research.ranking.completed",
        "source": "rank_discovered_repos.py",
        "payload": ranked,
        "recipients": ["emperor", "researcher", "cto"]
    }
    ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
    (bus_dir / f"{ts}_research.ranking.completed.json").write_text(json.dumps(event, indent=2))
    print(json.dumps(ranked, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
