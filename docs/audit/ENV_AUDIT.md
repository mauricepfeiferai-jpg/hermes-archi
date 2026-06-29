# ENV AUDIT
**Date:** 2026-06-28  
**Scope:** All .env.example files in hermes-archi

---

## Summary

| File | Status | Keys needed |
|------|--------|------------|
| `control-plane/.env.example` | ✅ Well-defined | Stripe keys + storage paths |
| `control-plane/telegram/.env.example` | ✅ Well-defined | BOT_TOKEN + Topic IDs |
| `telegram/.env.example` | ⚠️ Legacy/duplicate | TELEGRAM_BOT_TOKEN (same as above) |
| `trading/integrations/polymarket/.env.example` | 🔴 Real keys needed | POLYGON_PRIVATE_KEY, ANTHROPIC_API_KEY, TAVILY_API_KEY |
| `model-layer/docker.env.example` | ⚠️ Wrong file | Leftover from upstream app (Prisma/Neo4j/PostHog) — not relevant to hermes-archi |

---

## Keys Required — Grouped by Priority

### 🔴 Required to Run (nothing works without these)

| Key | Where | Source |
|-----|-------|--------|
| `TELEGRAM_BOT_TOKEN` | `control-plane/telegram/.env` | @BotFather → @HermesHecate1337bot token |
| `TELEGRAM_TOPIC_JARVIS` | `control-plane/telegram/.env` | From Telegram group topic links |
| `TELEGRAM_TOPIC_HERMES` | `control-plane/telegram/.env` | From Telegram group topic links |
| `TELEGRAM_TOPIC_OPENCLAW` | `control-plane/telegram/.env` | From Telegram group topic links |
| `TELEGRAM_TOPIC_HARVEY` | `control-plane/telegram/.env` | From Telegram group topic links |
| `TELEGRAM_ADMIN_ID` | `control-plane/telegram/.env` | Maurice's Telegram user ID (8531161985) |

### 🟡 Required for Trading

| Key | Where | Source |
|-----|-------|--------|
| `POLYGON_PRIVATE_KEY` | `trading/integrations/polymarket/.env` | Polygon wallet (PAPER_MODE=true by default — safe) |
| `ANTHROPIC_API_KEY` | `trading/integrations/polymarket/.env` | Anthropic console |
| `TAVILY_API_KEY` | `trading/integrations/polymarket/.env` | tavily.com |

### 🟢 Pre-filled / Safe Defaults (no action needed)

| Key | Default | Notes |
|-----|---------|-------|
| `OLLAMA_URL` | `http://localhost:11434` | Correct for local Ollama |
| `JARVIS_MODEL` | `qwen3:30b-a3b` | Aligned with current setup |
| `OPENCLAW_MODEL` | `qwen3:30b-a3b` | Aligned |
| `HARVEY_MODEL` | `deepseek-r1:32b` | Check if installed locally |
| `PAPER_MODE` | `true` | Trading is safe — no real funds |
| All ports (188xx range) | Defined | No conflicts with :18789 legacy |

### 🔵 Optional / Monetization (can skip for now)

| Key | File | Notes |
|-----|------|-------|
| `STRIPE_PAYMENT_LINK` | `control-plane/.env` | Harvey billing — skip until live |
| `STRIPE_WEBHOOK_SECRET` | `control-plane/.env` | Harvey billing — skip until live |
| `TELEGRAM_TARGET_CHANNEL` | `control-plane/telegram/.env` | Promo posts — optional |

---

## Issues Found

### 1. Duplicate Telegram .env.example
- `control-plane/telegram/.env.example` — correct, for Core4 topic routing
- `telegram/.env.example` — legacy, for the old Docker multi-agent stack

**Decision needed:** Which bot is active? (See Telegram Bot Selection approval)

### 2. model-layer/docker.env.example is the wrong file
This file belongs to the upstream Remix/Prisma/Neo4j app this code was extracted from.
It contains `POSTHOG_PROJECT_KEY`, `NEO4J_URI`, `SESSION_SECRET` — none of which are used by hermes-archi.

**Recommendation:** Delete or move to `legacy/`.

### 3. Storage paths need to exist
`control-plane/.env.example` references:
- `/var/lib/hermes/knowledge_graph.db`
- `/var/lib/jarvis/memory.db`
- `/var/lib/hermes/goals`
- `/var/lib/harvey/legal_usage`

These directories do not exist on Mac (they're Linux paths from Hetzner deploy).
For local Mac dev, these should be overridden to `~/.hermes/` paths.

---

## Recommended Action: Create one master .env for local Mac dev

```bash
# ~/.hermes/hermes-archi.env  (git-ignored, never committed)

TELEGRAM_BOT_TOKEN=<from @HermesHecate1337bot>
TELEGRAM_ADMIN_ID=8531161985
TELEGRAM_TOPIC_JARVIS=<from group>
TELEGRAM_TOPIC_HERMES=<from group>
TELEGRAM_TOPIC_OPENCLAW=<from group>
TELEGRAM_TOPIC_HARVEY=<from group>

OLLAMA_URL=http://localhost:11434
JARVIS_MODEL=qwen3:30b-a3b
OPENCLAW_MODEL=qwen3:30b-a3b
HARVEY_MODEL=deepseek-r1:32b

HERMES_KG_DB=~/.hermes/knowledge_graph.db
JARVIS_MEMORY_DB=~/.hermes/jarvis_memory.db
GOALS_DIR=~/.hermes/goals
HARVEY_USAGE_DIR=~/.hermes/legal_usage

LOG_LEVEL=INFO
```

Trading stays separate at `trading/integrations/polymarket/.env` — PAPER_MODE=true until manually flipped.

---

## Next Approval Line

```
APPROVE TELEGRAM BOT SELECTION
```
or
```
APPROVE LOCAL ENV CREATION
```
