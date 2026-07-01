#!/usr/bin/env python3
"""
Agent OS Dispatch Router
Routes tasks to the right agent runtime based on agent_registry.json.
Implements the neural network metaphor: task = signal, agent = neuron.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
REGISTRY = REPO / "agents" / "agent-os-harness" / "agent_registry.json"
BUS_DIR = REPO / "state" / "neural-bus"
DOPAMINE_DIR = REPO / "state" / "dopamine"


def load_registry():
    with open(REGISTRY) as f:
        return json.load(f)


def emit_event(event_type, source, payload, recipients=None):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    event = {
        "ts": ts,
        "type": event_type,
        "source": source,
        "payload": payload,
        "recipients": recipients or ["all"],
    }
    fname = f"{ts.replace(':', '-').replace('.', '-')}_{event_type}.json"
    with open(BUS_DIR / fname, "w") as f:
        json.dump(event, f, indent=2)
    return event


def dispatch_to_openclaw(agent_id, task, payload):
    """Send task to OpenClaw main agent via CLI."""
    message = json.dumps({"source": "dispatch", "agent": agent_id, "task": task, "payload": payload}, ensure_ascii=False)
    cmd = ["openclaw", "agent", "--agent", "main", "--message", message]
    if payload.get("local", False):
        cmd.append("--local")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-1000:],
            "rc": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch_to_hermes(skill_name, task):
    """Send task to Hermes as skill invocation."""
    cmd = ["hermes", "run", "--skill", skill_name, "--task", task]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-500:],
            "rc": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch_to_claude(prompt, workdir=None):
    """Send task to Claude Code non-interactive."""
    cmd = ["claude", "--no-interactive", "-p", prompt]
    try:
        cwd = Path(workdir) if workdir else REPO
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=cwd)
        return {
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-500:],
            "rc": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch_to_codex(prompt, workdir=None):
    """Send task to Codex non-interactive."""
    cmd = ["codex", "--no-interactive", "-q", prompt]
    try:
        cwd = Path(workdir) if workdir else REPO
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=cwd)
        return {
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-500:],
            "rc": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch_to_kimi(prompt):
    """Legacy alias: Kimi API is suspended (insufficient balance).
    Routes to Ollama Cloud deepseek-v4-flash:cloud via local Ollama HTTP API.
    """
    return dispatch_to_ollama_cloud(prompt, model="deepseek-v4-flash:cloud")


def dispatch_to_ollama_cloud(prompt, model="deepseek-v4-flash:cloud"):
    """Send task to Ollama Cloud via local Ollama HTTP API."""
    import requests
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return {
            "content": data.get("response", ""),
            "model": model,
            "eval_count": data.get("eval_count", 0),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch_to_ollama(model, prompt):
    """Send task to Ollama (cloud aliases per memory decision)."""
    cmd = ["ollama", "run", model, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-500:],
            "rc": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


def dispatch(agent_id, task, payload=None, prompt=None):
    registry = load_registry()
    agent = next((a for a in registry["agents"] if a["id"] == agent_id), None)
    if not agent and agent_id == "emperor":
        agent = registry.get("emperor")
    if not agent:
        return {"error": f"Agent {agent_id} not found"}
    if not agent.get("enabled", True):
        return {"error": f"Agent {agent_id} is disabled"}

    runtime = agent.get("runtime")
    result = None

    if runtime == "openclaw":
        result = dispatch_to_openclaw(agent_id, task, payload or {})
    elif runtime == "hermes-cli":
        result = dispatch_to_hermes(task, prompt or task)
    elif runtime == "claude-code":
        result = dispatch_to_claude(prompt or task)
    elif runtime == "codex-cli":
        result = dispatch_to_codex(prompt or task)
    elif runtime == "openai-api":
        result = dispatch_to_kimi(prompt or task)
    elif runtime == "ollama":
        model = (payload or {}).get("model", agent.get("models", ["glm-5.2:cloud"])[0])
        result = dispatch_to_ollama(model, prompt or task)
    elif runtime == "python":
        result = {"note": "python runtime dispatched", "agent": agent_id, "task": task}
    else:
        result = {"error": f"Unknown runtime {runtime}"}

    emit_event(
        "agent.dispatch.completed",
        "dispatch.py",
        {"agent_id": agent_id, "task": task, "result_summary": str(result)[:200]},
        recipients=[agent_id, "emperor", "dashboard"],
    )
    return result


def score_dopamine(event_type, payload):
    """Compute dopamine delta for a completed event."""
    score = 0.0
    if event_type == "code.completed":
        score += payload.get("files", 0) * 0.1
        score += payload.get("tests_passed", 0) * 2
        score += payload.get("commits", 0) * 1
        score += payload.get("merged_prs", 0) * 5
    elif event_type == "skill.created":
        score += 10
    elif event_type == "library.entry":
        score += 3
    elif event_type == "revenue":
        score += payload.get("amount", 0) * 50
    elif event_type == "agent.task.completed":
        score += 1
    return round(score, 2)


def update_dopamine(event_type, payload):
    DOPAMINE_DIR.mkdir(parents=True, exist_ok=True)
    score_file = DOPAMINE_DIR / "score.json"
    current = {"score": 0.0, "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
    if score_file.exists():
        with open(score_file) as f:
            current = json.load(f)

    delta = score_dopamine(event_type, payload)
    current["score"] = round(current.get("score", 0.0) + delta, 2)
    current["last_delta"] = delta
    current["last_event"] = event_type
    current["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    with open(score_file, "w") as f:
        json.dump(current, f, indent=2)

    history_file = DOPAMINE_DIR / "history.json"
    history = []
    if history_file.exists():
        with open(history_file) as f:
            history = json.load(f)
    history.append({"ts": current["last_updated"], "delta": delta, "score": current["score"], "event": event_type})
    with open(history_file, "w") as f:
        json.dump(history[-365:], f, indent=2)

    return current


def main():
    if len(sys.argv) < 2:
        print("Usage: dispatch.py [list | <agent_id> <task> [--payload JSON]]")
        sys.exit(1)

    if sys.argv[1] == "list":
        registry = load_registry()
        print("=== Emperor ===")
        print(json.dumps(registry.get("emperor"), indent=2))
        print("\n=== Agents ===")
        for a in registry.get("agents", []):
            status = "enabled" if a.get("enabled", True) else "disabled"
            print(a.get("id", "?") + " (" + a.get("runtime", "?") + ") [" + status + "] -- " + a.get("role", "?"))
        return

    if len(sys.argv) < 3:
        print("Usage: dispatch.py [list | <agent_id> <task> [--payload JSON]]")
        sys.exit(1)

    agent_id = sys.argv[1]
    task = sys.argv[2]
    payload = {}
    if "--payload" in sys.argv:
        idx = sys.argv.index("--payload")
        payload = json.loads(sys.argv[idx + 1])

    result = dispatch(agent_id, task, payload)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
