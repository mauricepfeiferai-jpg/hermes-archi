# Agent OS Harness

Dispatch router + silver loop harness for Maurice's AI Empire.

## Files

| File | Purpose |
|---|---|
| `agent_registry.json` | All connected agents and runtimes |
| `dispatch.py` | Route task to agent (Hermes, OpenClaw, Claude, Codex, Ollama Cloud, local Ollama) |
| `silver_loop_harness.py` | Run fixed reflex loops |

## Usage

```bash
# List all agents
python3 agents/agent-os-harness/dispatch.py list

# Dispatch to Hermes
python3 agents/agent-os-harness/dispatch.py hermes_orchestrator "review code" --payload '{"skill":"review-output"}'

# Dispatch to OpenClaw
python3 agents/agent-os-harness/dispatch.py openclaw_main "check disk" --payload '{"tool":"exec","cmd":"df -h"}'

# Dispatch to Ollama Cloud (legacy kimi_api alias)
python3 agents/agent-os-harness/dispatch.py kimi_api "Summarize this: ..." # routes to Ollama Cloud

# Run silver loops
python3 agents/agent-os-harness/silver_loop_harness.py list
python3 agents/agent-os-harness/silver_loop_harness.py run
```

## Neural Bus

Every dispatch writes a JSON event to `state/neural-bus/`.

## Dopamine

Call `dispatch.py update_dopamine` from scripts when code completes.
