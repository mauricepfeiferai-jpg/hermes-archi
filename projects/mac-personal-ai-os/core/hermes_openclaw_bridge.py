#!/usr/bin/env python3
"""Bridge between Hermes engine and OpenClaw gateway."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import mqc_skill_runner

HOME = Path.home()
DISPATCH = HOME / "ai-empire" / "projects" / "hermes-archi" / "agents" / "agent-os-harness" / "dispatch.py"


def classify_intent(text: str) -> dict:
    t = text.lower()
    intents = [
        ("morning_routine", ["morgen", "morning", "tagesplan", "daily", "routine", "starte meinen tag", "starte den tag", "tag starten", "executive briefing", "briefing"]),
        ("research", ["recherch", "finde", "suche", "research", "look up", "summarize"]),
        ("engineering", ["code", "programm", "implement", "deploy", "fix", "bug", "test"]),
        ("business", ["verkauf", "kunde", "produkt", "umsatz", "sales", "launch", "preis"]),
        ("legal", ["recht", "anwalt", "frist", "beweis", "klage", "legal"]),
        ("bma", ["bma", "brandmelde", "angebot", "norm", "vds"]),
        ("system", ["status", "speicher", "disk", "cron", "backup", "health"]),
        ("general", []),
    ]
    for intent, keywords in intents:
        if any(k in t for k in keywords):
            return {"intent": intent, "confidence": "rule"}
    return {"intent": "general", "confidence": "fallback"}


def route_to_hermes(intent: dict, text: str) -> dict:
    mapping = {
        "morning_routine": ("executive_assistant", "executive_morning_routine"),
        "research": ("researcher", "research_scan"),
        "engineering": ("engineer", "engineer_ship"),
        "business": ("sales", "sales_inbox"),
        "legal": ("legal_assistant", "scan"),
        "bma": ("bma_assistant", "check_norm"),
        "system": ("cto", "tech_health"),
        "general": ("hermes_orchestrator", "route"),
    }
    agent, action = mapping.get(intent["intent"], ("hermes_orchestrator", "route"))

    if action in mqc_skill_runner.SKILL_MAP:
        skill_result = mqc_skill_runner.run_skill(action, {"text": text})
        return {"agent": agent, "action": action, "runtime": "mqc_skill_runner", "skill_result": skill_result, "text": text}

    if DISPATCH.exists():
        try:
            result = subprocess.run(
                ["python3", str(DISPATCH), agent, action, "--payload", json.dumps({"text": text})],
                capture_output=True, text=True, timeout=15
            )
            result_data = None
            try:
                result_data = json.loads(result.stdout.strip())
            except Exception:
                result_data = None
            return {
                "agent": agent, "action": action, "runtime": "dispatch.py",
                "dispatch_stdout": result.stdout[:2000] if not result_data else None,
                "dispatch_parsed": result_data,
                "dispatch_stderr": result.stderr[:500] if result.stderr else None,
                "dispatch_returncode": result.returncode,
                "text": text,
            }
        except Exception as e:
            return {"agent": agent, "action": action, "error": str(e), "text": text, "note": "dispatch exception"}
    else:
        return {"agent": agent, "action": action, "note": "dispatch.py not found", "text": text}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    intent = classify_intent(args.text)
    result = route_to_hermes(intent, args.text)
    out = {"intent": intent, "result": result}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"Intent: {intent['intent']}")
        print(f"Agent:  {result['agent']}")
        print(f"Action: {result['action']}")
        if result.get("runtime"):
            print(f"Runtime: {result['runtime']}")
        if result.get("skill_result"):
            sr = result["skill_result"]
            print(f"Status: {sr.get('status')}")
            print(sr.get("stdout", "")[:1500])
            if sr.get("stderr"):
                print(f"Stderr: {sr['stderr'][:200]}")
        elif result.get("dispatch_parsed"):
            print(json.dumps(result["dispatch_parsed"], ensure_ascii=False, indent=2)[:1500])
        if result.get("error"):
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
