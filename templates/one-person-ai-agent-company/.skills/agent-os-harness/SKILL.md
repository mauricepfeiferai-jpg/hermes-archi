# Agent OS Harness Skill

Use this skill when the user wants to:
- Dispatch a task to a specific agent
- Run the silver loop harness
- Check dopamine score or neural bus
- Connect OpenClaw, Hermes, Claude, Codex, Ollama Cloud, local Ollama

## Available Agents

- `emperor` — orchestrator
- `openclaw_main` — local tool/UI agent
- `hermes_orchestrator` — skill runtime
- `claude_code` — deep engineering
- `codex` — batch engineering
- `kimi_api` — fast reasoning (legacy alias, now Ollama Cloud)
- `ollama_cloud` — local/cloud fallback
- `researcher` — discovery agent
- `ceo`, `cto`, `engineer`, `writer`, `sales`, `youtube_operator`, `loop_agent`

## Commands

```bash
python3 agents/agent-os-harness/dispatch.py <agent_id> "<task>" [--payload JSON]
python3 agents/agent-os-harness/silver_loop_harness.py [list|run|react]
```

## Dopamine Rule

When an agent completes code that is committed, call:

```bash
python3 -c "from agents.agent_os_harness.dispatch import update_dopamine; update_dopamine('code.completed', {'files':3, 'tests_passed':5, 'commits':1})"
```

## Safety

- Do not install new packages without approval.
- Do not push to production without approval.
- Do not auto-fallback to cloud models.
