#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

repo = Path.home() / "ai-empire" / "projects" / "hermes-archi"
out = repo / "templates" / "one-person-ai-agent-company" / "dashboard" / "data.json"

score = json.loads((repo / "state" / "dopamine" / "score.json").read_text()) if (repo / "state" / "dopamine" / "score.json").exists() else {"score": 0, "streak": 0, "homeostasis_threshold": 0}
neural_count = len(list((repo / "state" / "neural-bus").glob("*.json")))
loops = len(list((repo / "ops" / "cron").glob("*.sh")))
agents = json.loads((repo / "agents" / "agent-os-harness" / "agent_registry.json").read_text())["agents"]
skills = json.loads((repo / "state" / "skills" / "registry.json").read_text())["count"] if (repo / "state" / "skills" / "registry.json").exists() else 0
repos = json.loads((repo / "09_LIBRARY" / ".indices" / "github_library_index.json").read_text())["count"] if (repo / "09_LIBRARY" / ".indices" / "github_library_index.json").exists() else 0
nuggets = json.loads((repo / "state" / "libraries" / ".indices" / "knowledge_index.json").read_text())["count"] if (repo / "state" / "libraries" / ".indices" / "knowledge_index.json").exists() else 0
lessons = json.loads((repo / "loop" / "lessons.json").read_text()) if (repo / "loop" / "lessons.json").exists() else []

proposals = []
prop_dir = repo / "state" / "adaptive-loop-engine"
if prop_dir.exists():
    files = sorted(prop_dir.glob("report_*.json"))
    if files:
        proposals = json.loads(files[-1].read_text()).get("proposals", [])


# X Trends summary
x_trends_count = 0
x_latest_titles = []
x_trend_files = sorted((repo / "state" / "x").glob("trends_*.json"), reverse=True)
if x_trend_files:
    try:
        x_data = json.loads(x_trend_files[0].read_text())
        x_trends_count = x_data.get("total_items", 0)
        titles = []
        for r in x_data.get("results", []):
            for item in r.get("items", []):
                t = item.get("title")
                if t and t not in titles:
                    titles.append(t)
        x_latest_titles = titles[:5]
    except Exception:
        pass

data = {
    "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "agents": [a["id"] for a in agents],
    "loops": loops,
    "skills": skills,
    "github_repos": repos,
    "knowledge_nuggets": nuggets,
    "dopamine_score": score["score"],
    "dopamine_streak": score["streak"],
    "dopamine_threshold": score.get("homeostasis_threshold", 0),
    "neural_events": neural_count,
    "lessons": len(lessons),
    "status": "LIVE",
    "last_commit": "ea3de3e",
    "proposals": proposals,
                "x_trends_24h": x_trends_count,
        "x_latest_titles": x_latest_titles,
}
out.write_text(json.dumps(data, indent=2))
print(json.dumps(data, indent=2))
