#!/usr/bin/env python3
"""Generate a learned Python skill from a DEMONSTRATION.md file."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MQC = HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os"
DEMO_DIR = MQC / "demonstrations"
SKILL_DIR = MQC / "learned-skills"


def parse_demonstration(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    meta = {}
    steps = []
    mode = None
    for line in lines:
        if line.startswith("# Demonstration:"):
            meta["name"] = line.replace("# Demonstration:", "").strip()
        elif line.startswith("- skill_name:"):
            meta["skill_name"] = line.split(":", 1)[1].strip()
        elif line.startswith("- trigger_phrases:"):
            meta["trigger_phrases"] = [p.strip() for p in line.split(":", 1)[1].split(",")]
        elif line.startswith("- agent:"):
            meta["agent"] = line.split(":", 1)[1].strip()
        elif line.startswith("- red_gates:"):
            meta["red_gates"] = [g.strip() for g in line.split(":", 1)[1].split(",")]
        elif line.startswith("## Goal"):
            mode = "goal"
            continue
        elif line.startswith("## Steps"):
            mode = "steps"
            continue
        elif line.startswith("## Example Invocation"):
            mode = None
            continue
        elif line.startswith("## Data Sources"):
            mode = None
            continue
        elif mode == "goal" and line.strip():
            meta["goal"] = line.strip()
            mode = None
        elif mode == "steps" and re.match(r"^\d+\.\s+", line):
            steps.append(re.sub(r"^\d+\.\s+", "", line))

    meta["steps"] = steps
    return meta


def generate_skill(demo_path: Path, force: bool = False) -> dict:
    meta = parse_demonstration(demo_path)
    skill_name = meta.get("skill_name") or slugify(meta.get("name", "learned_skill"))
    target = SKILL_DIR / f"{skill_name}.py"

    if target.exists() and not force:
        return {"success": False, "path": str(target), "error": "Skill already exists. Use --force to overwrite."}

    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/usr/bin/env python3",
        f'"""Learned skill: {meta.get("name", skill_name)}"""',
        "import json",
        "import sys",
        "from pathlib import Path",
        "",
        f"# Generated from {demo_path.name} at {datetime.now().isoformat()}",
        "",
        "HOME = Path.home()",
        'MQC = HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os"',
        "sys.path.insert(0, str(MQC / 'core'))",
        "import mqc_skill_runner",
        "",
        "SKILL_NAME = " + repr(skill_name),
        "TRIGGER_PHRASES = " + repr(meta.get("trigger_phrases", [skill_name])),
        "AGENT = " + repr(meta.get("agent", "executive_assistant")),
        "RED_GATES = " + repr(meta.get("red_gates", [])),
        "",
        "def run(payload: dict = None) -> dict:",
        '    payload = payload or {}',
        '    results = []',
    ]
    for step in meta.get("steps", []):
        # Map some natural step patterns to skill calls
        lowered = step.lower()
        if any(k in lowered for k in ["mail", "email", "posteingang", "ungelesen"]):
            lines.append('    results.append({"step": ' + repr(step) + ', "result": mqc_skill_runner.run_skill("read_mail", {"limit": 10})})')
        elif any(k in lowered for k in ["calendar", "termin", "heute", "besprechung"]):
            lines.append('    results.append({"step": ' + repr(step) + ', "result": mqc_skill_runner.run_skill("read_calendar", {"days": 1})})')
        elif any(k in lowered for k in ["messages", "nachricht", "sms", "imessage", "chat"]):
            lines.append('    results.append({"step": ' + repr(step) + ', "result": mqc_skill_runner.run_skill("read_messages", {"limit": 10})})')
        elif any(k in lowered for k in ["web", "suche", "recherch", "internet"]):
            query = payload.get("text", "")
            lines.append(f'    results.append({{"step": {repr(step)}, "result": mqc_skill_runner.run_skill("web_search", {{"text": payload.get("text", "")}})}})')
        elif any(k in lowered for k in ["speicher", "memory", "aktualisier", "update"]):
            lines.append('    results.append({"step": ' + repr(step) + ', "result": mqc_skill_runner.run_skill("update_memory", {})})')
        else:
            lines.append(f'    results.append({{"step": {repr(step)}, "result": None}})')
    lines += [
        '    return {"success": True, "skill": SKILL_NAME, "agent": AGENT, "results": results}',
        "",
        "if __name__ == '__main__':",
        '    import argparse',
        '    p = argparse.ArgumentParser()',
        '    p.add_argument("--payload", default="{}")',
        '    args = p.parse_args()',
        '    payload = json.loads(args.payload)',
        '    print(json.dumps(run(payload), ensure_ascii=False, indent=2))',
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
    return {"success": True, "path": str(target), "skill_name": skill_name}


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[-\s]+", "_", s).strip("_")
    return s[:60]


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC learned skill generator")
    parser.add_argument("demo", help="Path to DEMONSTRATION.md")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    demo_path = Path(args.demo).expanduser()
    if not demo_path.exists():
        demo_path = DEMO_DIR / demo_path.name
    result = generate_skill(demo_path, force=args.force)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("success"):
            print(f"Generated skill: {result.get('path')}")
        else:
            print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
