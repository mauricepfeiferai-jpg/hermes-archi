# Galaxia Friends Agents — Legacy Archive

These are the original Galaxia OS agents from the Friends-themed orchestration
layer. Archived here as part of the Core4 consolidation (Phase 5).

| Agent   | Role                     | Model (original)        |
|---------|--------------------------|-------------------------|
| Monica  | CEO / Orchestrator       | ollama/glm4:9b-chat     |
| Chandler| Sales & Marketing        | ollama/glm4:9b-chat     |
| Dwight  | Research Lead            | ollama/glm4:9b-chat     |
| Kelly   | Content Creator          | ollama/glm4:9b-chat     |
| Pam     | Newsletter & Products    | ollama/glm4:9b-chat     |
| Ross    | YouTube & Video          | ollama/glm4:9b-chat     |
| Ryan    | Code Engineer            | ollama/glm4:9b-chat     |

## Core4 Mapping

| Galaxia Agent          | Core4 Replacement                      |
|------------------------|----------------------------------------|
| Monica (Orchestrator)  | Hermes (orchestration + goal tracking) |
| Chandler/Kelly/Pam/Ross| OpenClaw (content-engine, youtube-factory, x-twitter-browser) |
| Dwight (Research)      | Jarvis (memory + knowledge base)       |
| Ryan (Code)            | OpenClaw (pi-coder skill)              |
| Harvey                 | Harvey (legal — new, no prior)         |

## Status

- `config.json` — original agent spec preserved for reference
- Skills moved to `openclaw/workspace/skills/`
- Not deleted — may be re-activated if Core4 agents need per-persona routing
