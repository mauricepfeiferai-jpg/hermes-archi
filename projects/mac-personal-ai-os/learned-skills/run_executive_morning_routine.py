#!/usr/bin/env python3
"""Learned skill: Executive Assistant morning routine."""
import json
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
REPO = HOME / "ai-empire" / "projects" / "hermes-archi"
MEM = HOME / ".openclaw" / "workspace" / "ai-empire" / "memory"
sys.path.insert(0, str(HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os" / "core"))
import mqc_skill_runner


def run_task(task_name: str):
    return mqc_skill_runner.run_skill(task_name, {})


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def read_next():
    path = MEM / "NEXT.md"
    if not path.exists():
        return "No NEXT.md found"
    lines = path.read_text().splitlines()
    bullets = []
    for line in lines:
        if line.startswith("## "):
            if bullets:
                break
            bullets = [line]
        elif bullets and line.startswith(("- ", "1. ", "2. ", "3. ", "4. ", "5. ")):
            bullets.append(line)
    return "\n".join(bullets[:6])


def main():
    date = datetime.now().strftime("%Y-%m-%d")
    queue_result = run_task("morning_queue")
    health_result = run_task("tech_health")
    queue_data = load_json(REPO / "state" / "ceo" / f"morning_queue_{date}.json")
    health_data = load_json(REPO / "state" / "cto" / f"tech_health_{date}.json")
    priorities = queue_data.get("priorities", [])[:3]
    alerts = health_data.get("alerts", [])
    priority_line = "Priorities: " + " | ".join(f"#{p['rank']} {p['action']} ({p['owner']})" for p in priorities) if priorities else "Priorities: no queue found"
    status_line = f"System: {health_data.get('disk_gb_free', '?')} GB free"
    if alerts:
        status_line += f", {len(alerts)} alert(s): " + ", ".join(alerts)
    else:
        status_line += ", all green"
    next_text = read_next()
    next_line = "Next: " + " | ".join(p.strip()[2:] for p in next_text.splitlines()[1:3]) if next_text else "Next: nothing in NEXT.md"
    briefing = f"{priority_line}\n{status_line}\n{next_line}"
    print(briefing)


if __name__ == "__main__":
    main()
