"""Obsidian Exporter — Core4 state → markdown vault.

The view-side counterpart to importer.py. Writes Core4's live state into a
plain Obsidian vault so Maurice sees everything in one place:

  - Hermes goals (Kanban) → 03_Goals/
  - Knowledge-base digest (imported facts by source) → 02_Knowledge/
  - Agent health snapshot + dashboard → 00_DASHBOARD.md

Plain markdown, zero lock-in. Idempotent (overwrites managed files only).
Designed to run from the night job (cron) or manually.

Usage:
    python obsidian_export.py --vault ~/Obsidian/AI-Empire-Vault
    OBSIDIAN_VAULT=~/vault python obsidian_export.py
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DB_PATH = Path(os.getenv("JARVIS_MEMORY_DB", "/var/lib/jarvis/memory.db"))
HERMES_URL = os.getenv("HERMES_URL", "http://127.0.0.1:18790")
SUBDIR = "EMPIRE_CORE4"  # all managed notes live here (safe to regenerate)


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime())


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _http_json(url: str, timeout: float = 5.0) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def export_goals(vault: Path) -> int:
    data = _http_json(f"{HERMES_URL}/goals")
    if not data:
        return 0
    goals = data.get("goals", [])
    by_status: dict[str, list] = {}
    for g in goals:
        by_status.setdefault(g.get("status", "unknown"), []).append(g)

    lines = ["---", "type: core4-goals", f"updated: {_now()}", "---", "",
             "# Hermes Goals (Kanban)", ""]
    order = ["in_progress", "review", "todo", "blocked", "done", "cancelled"]
    for status in order + [s for s in by_status if s not in order]:
        items = by_status.get(status, [])
        if not items:
            continue
        lines.append(f"## {status} ({len(items)})")
        for g in items:
            prio = g.get("priority", "")
            owner = g.get("owner_agent", "")
            lines.append(f"- **{g.get('title','(no title)')}** "
                         f"`{prio}` → {owner}  ^{g.get('id','')}")
        lines.append("")
    _write(vault / SUBDIR / "03_Goals" / "Hermes_Goals.md", "\n".join(lines))
    return len(goals)


def export_knowledge(vault: Path) -> int:
    if not DB_PATH.exists():
        return 0
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        total = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        by_label = conn.execute(
            "SELECT COALESCE(label,'(none)') l, COUNT(*) c FROM facts GROUP BY l ORDER BY c DESC"
        ).fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return 0

    lines = ["---", "type: core4-knowledge", f"updated: {_now()}", "---", "",
             "# Wissensspeicher (Jarvis Memory)", "",
             f"**Total facts:** {total}", "", "## Nach Quelle", ""]
    for label, c in by_label:
        lines.append(f"- {label}: **{c}**")
    lines += ["", "## Suche",
              "Jarvis durchsucht diese Basis automatisch bei jeder Anfrage (FTS5).",
              "Direktsuche auf dem Server:",
              "```bash",
              "python control-plane/jarvis/runtime/importer.py --stats",
              "```"]
    _write(vault / SUBDIR / "02_Knowledge" / "Wissensspeicher.md", "\n".join(lines))

    # Recent samples per label for browsability
    try:
        recent = conn.execute(
            "SELECT label, source, text, ts FROM facts ORDER BY id DESC LIMIT 50"
        ).fetchall()
        rlines = ["---", "type: core4-knowledge-recent", f"updated: {_now()}", "---", "",
                  "# Zuletzt importiert (50)", ""]
        for label, source, text, ts in recent:
            rlines.append(f"### {source or label} · {ts}")
            rlines.append(text[:500])
            rlines.append("")
        _write(vault / SUBDIR / "02_Knowledge" / "Zuletzt_importiert.md", "\n".join(rlines))
    except sqlite3.OperationalError:
        pass
    conn.close()
    return total


def export_health(vault: Path) -> dict:
    agents = _http_json(f"{HERMES_URL}/agents") or {}
    return agents


def export_dashboard(vault: Path, goal_count: int, fact_count: int, agents: dict) -> None:
    agent_list = agents.get("agents", [])
    lines = ["---", "type: core4-dashboard", f"updated: {_now()}", "---", "",
             "# Core4 Dashboard", "",
             "> Auto-generiert von Core4. Nicht manuell editieren (wird überschrieben).",
             "", "## System", ""]
    if agent_list:
        for a in agent_list:
            icon = "✅" if a.get("status") == "healthy" else "⚠️"
            lines.append(f"- {icon} **{a.get('name')}** — {a.get('url','')}")
    else:
        lines.append("- ⚠️ Hermes nicht erreichbar (Daemons gestartet?)")
    lines += ["", "## Zahlen", "",
              f"- Goals: **{goal_count}**",
              f"- Wissens-Facts: **{fact_count}**",
              "", "## Links", "",
              f"- [[{SUBDIR}/03_Goals/Hermes_Goals|Goals (Kanban)]]",
              f"- [[{SUBDIR}/02_Knowledge/Wissensspeicher|Wissensspeicher]]",
              f"- [[{SUBDIR}/02_Knowledge/Zuletzt_importiert|Zuletzt importiert]]",
              ""]
    _write(vault / SUBDIR / "00_DASHBOARD.md", "\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description="Export Core4 state to an Obsidian vault")
    ap.add_argument("--vault", type=Path, default=os.getenv("OBSIDIAN_VAULT"),
                    help="Path to Obsidian vault root")
    args = ap.parse_args()
    if not args.vault:
        ap.error("provide --vault or set OBSIDIAN_VAULT")
    vault = Path(args.vault).expanduser()
    vault.mkdir(parents=True, exist_ok=True)

    print(f"Exporting Core4 → {vault / SUBDIR}")
    goals = export_goals(vault)
    facts = export_knowledge(vault)
    agents = export_health(vault)
    export_dashboard(vault, goals, facts, agents)
    print(f"  Goals: {goals}  Facts: {facts}  "
          f"Agents: {len(agents.get('agents', []))}")
    print(f"Done. Open Obsidian → {SUBDIR}/00_DASHBOARD.md")


if __name__ == "__main__":
    main()
