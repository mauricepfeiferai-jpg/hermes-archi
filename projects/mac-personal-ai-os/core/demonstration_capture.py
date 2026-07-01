#!/usr/bin/env python3
"""Capture a user demonstration and write a DEMONSTRATION.md for skill generation."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MQC = HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os"
DEMO_DIR = MQC / "demonstrations"


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[-\s]+", "_", s).strip("_")
    return s[:60]


def capture(name: str, steps: list[str], context: dict = None) -> dict:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    slug = slugify(name)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"DEMO_{slug}_{timestamp}.md"
    path = DEMO_DIR / filename

    ctx = context or {}
    lines = [
        f"# Demonstration: {name}",
        "",
        f"- captured_at: {datetime.now().isoformat()}",
        f"- skill_name: {slug}",
        f"- trigger_phrases: {', '.join(ctx.get('trigger_phrases', [name]))}",
        f"- agent: {ctx.get('agent', 'executive_assistant')}",
        f"- red_gates: {', '.join(ctx.get('red_gates', ['send_email', 'delete_file']))}",
        "",
        "## Goal",
        ctx.get("goal", f"Execute the learned routine '{name}' step by step."),
        "",
        "## Steps",
    ]
    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}")
    lines += [
        "",
        "## Example Invocation",
        f"- User: \"{ctx.get('invocation', name)}\"",
        "",
        "## Data Sources",
    ]
    for ds in ctx.get("data_sources", []):
        lines.append(f"- {ds}")
    lines += [
        "",
        "## Notes",
        ctx.get("notes", "Captured by MQC demonstration capture."),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "success": True,
        "path": str(path),
        "skill_name": slug,
        "steps": len(steps),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC demonstration capture")
    parser.add_argument("name", help="Name of the routine/skill")
    parser.add_argument("--steps", default="", help="Comma-separated steps")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    result = capture(args.name, steps)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Captured: {result.get('path')}")


if __name__ == "__main__":
    main()
