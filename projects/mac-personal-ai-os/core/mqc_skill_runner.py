#!/usr/bin/env python3
"""Fast local skill runner for MQC-assigned tasks."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

HOME = Path.home()
REPO = HOME / "ai-empire" / "projects" / "hermes-archi"
TEMPLATE = REPO / "templates" / "one-person-ai-agent-company"
MQC = HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os"
CONNECTORS = MQC / "core" / "connectors"

# Auto-discover learned skills at import time
LEARNED_SKILLS_DIR = MQC / "learned-skills"

def _discover_learned_skills():
    discovered = {}
    if not LEARNED_SKILLS_DIR.exists():
        return discovered
    for py_file in sorted(LEARNED_SKILLS_DIR.glob("*.py")):
        name = py_file.stem
        if name.startswith("_"):
            continue
        discovered[name] = {
            "cmd": ["python3", str(py_file), "--payload", "{}"],
            "cwd": str(MQC),
            "passthrough_payload": True,
            "learned": True,
        }
    return discovered


SKILL_MAP = {
    "morning_queue": {
        "cmd": ["bash", str(TEMPLATE / ".skills" / "run-morning-queue" / "driver.sh")],
        "cwd": str(TEMPLATE),
        "needs_queue": True,
    },
    "generate_morning_queue": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "06-ceo-daily-goals.sh")],
        "cwd": str(REPO),
    },
    "tech_health": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "07-cto-tech-health.sh")],
        "cwd": str(REPO),
    },
    "engineer_ship": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "08-engineer-ship.sh")],
        "cwd": str(REPO),
    },
    "research_scan": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "09-researcher-scan.sh")],
        "cwd": str(REPO),
    },
    "writer_content": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "10-writer-content.sh")],
        "cwd": str(REPO),
    },
    "sales_inbox": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "11-sales-inbox.sh")],
        "cwd": str(REPO),
    },
    "ops_backup": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "19-ops-backup-health.sh")],
        "cwd": str(REPO),
    },
    "daily_review": {
        "cmd": ["bash", str(REPO / "ops" / "cron" / "20-loop-review.sh")],
        "cwd": str(REPO),
    },
    "read_mail": {
        "cmd": ["python3", str(CONNECTORS / "mail_connector.py"), "--json", "--limit", "10"],
        "cwd": str(MQC),
        "passthrough_flags": ["--limit"],
    },
    "read_calendar": {
        "cmd": ["python3", str(CONNECTORS / "calendar_connector.py"), "--json", "--days", "30"],
        "cwd": str(MQC),
        "passthrough_flags": ["--days"],
    },
    "read_messages": {
        "cmd": ["python3", str(CONNECTORS / "messages_connector.py"), "--json", "--limit", "10"],
        "cwd": str(MQC),
        "passthrough_flags": ["--limit"],
    },
    "update_memory": {
        "cmd": ["python3", str(MQC / "learned-skills" / "memory_update_session_end.py")],
    },
    "executive_morning_routine": {
        "cmd": ["python3", str(MQC / "learned-skills" / "run_executive_morning_routine.py")],
    },

    "web_search": {
        "cmd": ["python3", str(MQC / "core" / "web_search.py"), "--json"],
        "cwd": str(MQC),
        "passthrough_query": True,
    },
}

# Merge discovered learned skills
SKILL_MAP.update(_discover_learned_skills())



def run_skill(task_name: str, payload: dict = None) -> dict:
    payload = payload or {}
    meta = SKILL_MAP.get(task_name)
    if not meta:
        return {"status": "unknown_task", "task": task_name, "known_tasks": list(SKILL_MAP.keys())}
    cmd = meta["cmd"]
    cwd = meta.get("cwd")
    if meta.get("passthrough_query"):
        query = payload.get("text", "")
        cmd = cmd + [query]
    if meta.get("passthrough_flags"):
        for flag in meta["passthrough_flags"]:
            key = flag.lstrip("-").replace("-", "_")
            value = payload.get(key)
            if value:
                if flag in cmd:
                    idx = cmd.index(flag)
                    cmd[idx + 1] = str(value)
                else:
                    cmd = cmd + [flag, str(value)]
    if meta.get("passthrough_payload"):
        payload_str = json.dumps(payload)
        cmd = [payload_str if c == "{}" else c.replace('"{}"', payload_str) for c in cmd]

    if meta.get("needs_queue"):
        date = datetime.now().strftime("%Y-%m-%d")
        queue_md = TEMPLATE / "ceo" / "outputs" / f"morning_queue_{date}.md"
        queue_json = REPO / "state" / "ceo" / f"morning_queue_{date}.json"
        if not queue_md.exists() and not queue_json.exists():
            gen_meta = SKILL_MAP.get("generate_morning_queue")
            if gen_meta:
                subprocess.run(gen_meta["cmd"], cwd=gen_meta.get("cwd"), capture_output=True, text=True, timeout=60)
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "task": task_name, "cmd": cmd, "cwd": cwd,
            "stdout": result.stdout[:3000], "stderr": result.stderr[:500],
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"status": "exception", "task": task_name, "error": str(e)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--payload", default="{}")
    args = parser.parse_args()
    payload = json.loads(args.payload)
    result = run_skill(args.task, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
