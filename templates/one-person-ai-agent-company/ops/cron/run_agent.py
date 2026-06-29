#!/usr/bin/env python3
"""
Agent runner for the one-person AI agent company template.

Stub mode: writes a structured placeholder.
Hermes mode: dispatches to Hermes CLI when HERMES_PATH is set.

Usage:
  python3 run_agent.py {agent} {task} --date YYYY-MM-DD --out path/to/output.md
"""

import argparse
import subprocess
import os
from datetime import datetime
from pathlib import Path

STUB_TEMPLATE = """# {agent_name} Output — {date}

**Task:** {task}
**Agent:** {agent_name}
**Started:** {now}
**Mode:** stub

## Inputs Read
{inputs}

## Work Done
{work}

## Output / Result
{result}

## Quality Gate Check
- [ ] {gate1}
- [ ] {gate2}

## Next Action
{next_action}

## Human Approval Needed?
{approval}
"""

AGENTS = {
    "ceo": {"name": "CEO Agent", "task": "Set daily top 3 priorities"},
    "cto": {"name": "CTO Agent", "task": "Run tech health check"},
    "engineer": {"name": "Engineer Agent", "task": "Ship next backlog item"},
    "researcher": {"name": "Researcher Agent", "task": "Daily market/trend scan"},
    "writer": {"name": "Writer Agent", "task": "Draft content piece"},
    "sales": {"name": "Sales Agent", "task": "Update pipeline and draft outbound"},
    "ops": {"name": "Ops Agent", "task": "Backup and system health"},
    "loop": {"name": "Loop Agent", "task": "Review day and propose patch"},
}

TASK_MAP = {
    "daily-goals": ("Set daily top 3 priorities", "- loop/outputs/daily_review_*.md\n- sales/outputs/pipeline_*.md"),
    "tech-health": ("Run tech health check", "- git status\n- disk usage\n- backup status"),
    "ship-next": ("Ship next backlog item", "- ceo/outputs/daily_goals_*.md\n- engineer/backlog/"),
    "scan": ("Daily market/trend scan", "- researcher/sources.json\n- previous briefs"),
    "draft": ("Draft content piece", "- researcher/outputs/daily_brief_*.md\n- ceo/outputs/daily_goals_*.md"),
    "inbox": ("Update pipeline and draft outbound", "- sales/inbox/*.md\n- sales/crm.json"),
    "outbound": ("Draft outbound messages", "- researcher/outputs/daily_brief_*.md\n- sales/crm.json"),
    "backup-health": ("Backup and system health", "- configured backup paths\n- disk/cron status"),
    "review": ("Review day and classify failures", "- all */outputs/daily_*_*.md"),
    "improve": ("Propose durable patch", "- loop/outputs/daily_review_*.md\n- loop/lessons.json"),
}

def hermes_dispatch(agent_key: str, task_key: str, out_path: Path, date: str):
    """Dispatch to Hermes CLI if available. Falls back to stub on failure."""
    hermes_bin = os.environ.get("HERMES_PATH", "hermes")
    agent = AGENTS.get(agent_key, {"name": agent_key.upper(), "task": task_key})
    task_name, inputs = TASK_MAP.get(task_key, (task_key, "- (none)"))

    prompt = f"""You are the {agent['name']} in a one-person AI agent company.
Today's date: {date}.
Your task: {task_name}.
Read the relevant inputs, do the work, and write the result to {out_path}.
Follow the quality gates in the agent job description.
If any destructive or production action is needed, write an approval request instead of executing.

Inputs to consider:
{inputs}

Output must be a Markdown report with these sections:
# {agent['name']} Output — {date}
## Inputs Read
## Work Done
## Output / Result
## Quality Gate Check
## Next Action
## Human Approval Needed?
"""

    cmd = [hermes_bin, "--yolo", "--safe-mode", "-z", prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0 and result.stdout.strip():
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(result.stdout, encoding="utf-8")
            print(f"Hermes wrote: {out_path}")
            return
    except Exception as e:
        print(f"Hermes dispatch failed ({e}), falling back to stub.")

    write_stub(agent_key, task_key, out_path, date)

def write_stub(agent_key, task_key, out_path, date):
    agent = AGENTS.get(agent_key, {"name": agent_key.upper(), "task": task_key})
    task_name, inputs = TASK_MAP.get(task_key, (task_key, "- (none)"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = STUB_TEMPLATE.format(
        agent_name=agent["name"],
        date=date,
        task=task_name,
        now=datetime.now().isoformat(),
        inputs=inputs,
        work="- Read inputs\n- Hermes CLI not dispatched (stub mode)\n- Placeholder output generated",
        result=f"[PLACEHOLDER] {agent['name']} completed '{task_name}' on {date}. Connect HERMES_PATH env to enable real Hermes dispatch.",
        gate1="Inputs verified",
        gate2="Output format matches template",
        next_action="Review output and route to next agent or human approval.",
        approval="No destructive action — no approval needed for stub run."
    )
    out_path.write_text(content, encoding="utf-8")
    print(f"Stub wrote: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Run an agent task")
    parser.add_argument("agent")
    parser.add_argument("task")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_path = Path(args.out)
    use_hermes = os.environ.get("HERMES_PATH") or os.system("which hermes > /dev/null 2>&1") == 0

    if use_hermes:
        hermes_dispatch(args.agent, args.task, out_path, args.date)
    else:
        write_stub(args.agent, args.task, out_path, args.date)

if __name__ == "__main__":
    main()
