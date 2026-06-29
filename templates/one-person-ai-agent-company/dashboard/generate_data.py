#!/usr/bin/env python3
"""
Generate dashboard data.json from agent outputs.
Run this after the daily cron cycle:
    python3 dashboard/generate_data.py
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "data.json"

AGENTS = ["ceo", "cto", "engineer", "researcher", "writer", "sales", "ops", "loop"]

def parse_date_from_filename(filename):
    # daily_goals_2026-06-29.md -> 2026-06-29
    stem = filename.stem
    if "_" in stem:
        parts = stem.split("_")
        for p in parts:
            if len(p) == 10 and p[4] == "-" and p[7] == "-":
                return p
    return None

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

    # Backup age: check ops output for today's backup
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
    }

    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
