#!/usr/bin/env python3
"""Learned skill: update memory files after a session."""
import argparse
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MEM_DIR = HOME / ".openclaw" / "workspace" / "ai-empire" / "memory"


def append_current(summary: str):
    return f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} — SESSION UPDATE\n- {summary}\n"


def append_decisions(rule: str):
    return f"\n{datetime.now().strftime('%Y-%m-%d')}:\n- {rule}\n"


def rewrite_next(steps: list):
    header = f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} — UPDATE\n"
    body = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return header + body + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft")
    parser.add_argument("--decision")
    parser.add_argument("--next", nargs="+")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    out = []
    if args.draft:
        out.append(("CURRENT.md", append_current(args.draft)))
    if args.decision:
        out.append(("DECISIONS.md", append_decisions(args.decision)))
    if args.next:
        out.append(("NEXT.md", rewrite_next(args.next)))
    if not out:
        print("Nothing to update. Use --draft, --decision, --next.")
        return
    if args.apply:
        for filename, content in out:
            path = MEM_DIR / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
        print("Memory updated.")
    else:
        print("DRAFT:")
        for filename, content in out:
            print(f"\n=== {filename} ===")
            print(content)


if __name__ == "__main__":
    main()
