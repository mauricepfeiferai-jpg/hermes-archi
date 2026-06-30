#!/usr/bin/env python3
"""
Generate dashboard data.json from agent outputs and Agent OS state.
Run this after the daily cron cycle:
    python3 dashboard/generate_data.py
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "data.json"
REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"

AGENTS = ["ceo", "cto", "engineer", "researcher", "writer", "sales", "ops", "loop"]


def parse_date_from_filename(filename):
    stem = filename.stem
    if "_" in stem:
        parts = stem.split("_")
        for p in parts:
            if len(p) == 10 and p[4] == "-" and p[7] == "-":
                return p
    return None


def load_agent_os_state():
    state = {
        "dopamine_score": 0,
        "dopamine_streak": 0,
        "dopamine_last_delta": 0,
        "neural_events_24h": 0,
        "latest_events": [],
        "library_repos": 0,
        "library_skills": 0,
        "library_nuggets": 0,
    }

    score_file = REPO / "state" / "dopamine" / "score.json"
    if score_file.exists():
        try:
            d = json.loads(score_file.read_text())
            state["dopamine_score"] = d.get("score", 0)
            state["dopamine_streak"] = d.get("streak", 0)
            state["dopamine_last_delta"] = d.get("last_delta", 0)
        except Exception:
            pass

    bus_dir = REPO / "state" / "neural-bus"
    if bus_dir.exists():
        events = []
        for f in sorted(bus_dir.glob("*.json"), reverse=True):
            try:
                ev = json.loads(f.read_text())
                events.append({"ts": ev.get("ts"), "type": ev.get("type"), "source": ev.get("source")})
            except Exception:
                pass
        state["neural_events_24h"] = len(events)
        state["latest_events"] = events[:10]

    for idx_dir, idx_name, key in [
        (REPO / "09_LIBRARY" / ".indices", "github_library_index.json", "library_repos"),
        (REPO / "state" / "libraries" / ".indices", "knowledge_index.json", "library_nuggets"),
    ]:
        p = idx_dir / idx_name
        if p.exists():
            try:
                d = json.loads(p.read_text())
                state[key] = d.get("count", 0)
            except Exception:
                pass

    skill_registry = REPO / "state" / "skills" / "registry.json"
    if skill_registry.exists():
        try:
            d = json.loads(skill_registry.read_text())
            state["library_skills"] = d.get("count", 0)
        except Exception:
            pass

    return state


def main():
    outputs = []
    for agent in AGENTS:
        out_dir = ROOT / agent / "outputs"
        if not out_dir.exists():
            continue
        for f in sorted(out_dir.glob("*.md"), reverse=True):
            date = parse_date_from_filename(f)
            if date:
                outputs.append({
                    "agent": agent,
                    "file": f.name,
                    "date": date,
                    "path": str(f.relative_to(ROOT)),
                })

    lessons_file = ROOT / "loop" / "lessons.json"
    lessons = 0
    if lessons_file.exists():
        try:
            lessons = len(json.loads(lessons_file.read_text(encoding="utf-8")))
        except Exception:
            pass

    backup_str = "Unknown"
    ops_out = ROOT / "ops" / "outputs"
    if ops_out.exists():
        for f in sorted(ops_out.glob("health_*.md"), reverse=True):
            date = parse_date_from_filename(f)
            if date:
                backup_str = date
                break

    data = {
        "generated_at": datetime.now().isoformat(),
        "agents": AGENTS,
        "outputs": sorted(outputs, key=lambda x: x["date"], reverse=True),
        "lessons": lessons,
        "backup": backup_str,
        "agent_os": load_agent_os_state(),
    }

    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
