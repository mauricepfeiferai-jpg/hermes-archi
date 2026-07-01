#!/usr/bin/env python3
import json
import subprocess
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


# HIL status
hil = {"total_gate_checks": 0, "red_blocks": 0, "yellow_preparations": 0, "green_executions": 0}
hil_file = repo / "state" / "hil" / "status.json"
if hil_file.exists():
    try:
        hil = json.loads(hil_file.read_text())
    except Exception:
        pass


# Sales pipeline
sales = {
    "leads": 0,
    "contacted": 0,
    "replied": 0,
    "call_booked": 0,
    "paid": 0,
    "deals_value_usd": 0.0,
    "latest_actions": []
}
customers_file = repo / "state" / "sales" / "target_customers_2026-06-30.json"
if customers_file.exists():
    try:
        cdata = json.loads(customers_file.read_text())
        sales["leads"] = len(cdata.get("customers", []))
    except Exception:
        pass

# Count outreach sent by scanning neural bus for outreach events
for f in (repo / "state" / "neural-bus").glob("*outreach*"):
    try:
        e = json.loads(f.read_text())
        if e.get("type") == "sales.outreach.sent":
            sales["contacted"] += 1
    except Exception:
        pass

# Read manual pipeline state if exists
pipeline_file = repo / "state" / "sales" / "pipeline.json"
if pipeline_file.exists():
    try:
        pdata = json.loads(pipeline_file.read_text())
        for k in ["contacted", "replied", "call_booked", "paid", "deals_value_usd"]:
            sales[k] = max(sales[k], pdata.get(k, 0))
        sales["latest_actions"] = pdata.get("latest_actions", [])
    except Exception:
        pass

# Latest neural bus events (for dashboard feed)
latest_events = []
for f in sorted((repo / "state" / "neural-bus").glob("*.json"), reverse=True)[:10]:
    try:
        e = json.loads(f.read_text())
        latest_events.append({
            "ts": e.get("ts", ""),
            "type": e.get("type", ""),
            "source": e.get("source", ""),
        })
    except Exception:
        pass
latest_events.reverse()

# Recent outputs (for dashboard outputs list)
outputs = []
state_dirs = [
    repo / "state" / "x",
    repo / "state" / "libraries",
    repo / "state" / "09",
    repo / "state" / "10",
]
for d in state_dirs:
    if d.exists():
        for f in sorted(d.glob("*.json"), reverse=True)[:3]:
            try:
                outputs.append({
                    "agent": d.name,
                    "file": f.name,
                    "date": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                })
            except Exception:
                pass

# Sort outputs by date desc
outputs.sort(key=lambda x: x["date"], reverse=True)
outputs = outputs[:8]

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
    "last_commit": subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo, capture_output=True, text=True
        ).stdout.strip() or "unknown",
    "proposals": proposals,
                "sales_leads": sales["leads"],
        "sales_contacted": sales["contacted"],
        "sales_replied": sales["replied"],
        "sales_call_booked": sales["call_booked"],
        "sales_paid": sales["paid"],
        "sales_deals_value_usd": sales["deals_value_usd"],
        "sales_latest_actions": sales["latest_actions"],
                "hil_gate_checks": hil.get("total_gate_checks", 0),
        "hil_red_blocks": hil.get("red_blocks", 0),
        "hil_yellow": hil.get("yellow_preparations", 0),
        "hil_green": hil.get("green_executions", 0),
                "x_trends_24h": x_trends_count,
        "x_latest_titles": x_latest_titles,
        "latest_events": latest_events,
        "outputs": outputs,
}
out.write_text(json.dumps(data, indent=2))
print(json.dumps(data, indent=2))
