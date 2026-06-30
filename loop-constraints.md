# Loop Constraints — AI Empire Agent OS

## Global Denylist (no loop may do these)

- Delete production data or secrets
- Auto-merge to main
- Send money or process payments automatically
- Post to social accounts without human approval
- Modify .env or credential files
- rm -rf / recursive deletes
- Push to npm/pypi/gumroad without approval

## Human Gates

- L1 loops: report only
- L2 loops: suggest + verify, human approves action
- L3 loops: not enabled until 100 successful L2 runs

## MCP / Connector Scopes

- GitHub MCP: read + comment only (no merge)
- OpenClaw: query + notify only (no write without approval)
- Telegram: read + reply only in approved topics

## Cost Routing

- Verifier / classifier: cheap model
- Orchestrator / complex reasoning: strong model
- Fallback: local Ollama
