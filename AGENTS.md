# AGENTS.md — AI Empire / Hermes-Archi

## Build & Test Commands

```bash
# Verify site builds locally
python3 -m http.server 8000 --directory docs

# Check product deliverable
ls -lh releases/one-person-ai-agent-company-template.zip

# Audit loop readiness
npx @cobusgreyling/loop-audit . --suggest
```

## Review Norms

- All code changes via PR, never direct main push
- Tests / lint must pass before merge
- Secrets and credentials live in .env, never in git
- Product pages require human copy review\n