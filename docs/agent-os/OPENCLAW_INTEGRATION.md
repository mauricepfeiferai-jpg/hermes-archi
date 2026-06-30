# OpenClaw Integration — AI Empire Agent OS

## Status

- OpenClaw CLI: installed (`openclaw --version` → 2026.6.10)
- Main agent: `main` (default)
- Default model: `ollama/glm-5.2:cloud`
- Dispatch path: `agents/agent-os-harness/dispatch.py`

## How dispatch works

`dispatch.py openclaw_main <task> --payload JSON` calls:

```bash
openclaw agent --agent main --message {"source":"dispatch",...}
```

Result is captured and written to `state/neural-bus/`.

## Supported payloads

- `"local": true` → add `--local` flag
- Any JSON payload is forwarded inside the message

## Test command

```bash
cd ~/ai-empire/projects/hermes-archi
python3 agents/agent-os-harness/dispatch.py openclaw_main "Summarize current Agent OS status" --payload '{"local":true}'
```

## Neural bus recipients

Every OpenClaw dispatch emits `agent.dispatch.completed` to:
- The target agent
- `emperor`
- `dashboard`

## Next steps

- [ ] OpenClaw skill to read neural bus state
- [ ] Auto-routing: high-priority events trigger OpenClaw notification
- [ ] Mobile delivery via OpenClaw channels (when pairing works)
