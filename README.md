# Hermes-Archi

## Latest Additions (2026-06-29)
- **website/products/** — Live HTML landing pages for all 6 AI Empire products.
- **docs/ai-empire-products/** — GitHub Pages-ready mirror.
- **products/hermes-swarm-fan-out/** — Launch 5 sub-agents from one prompt.
- **products/chinese-ai-stack-migration/** — Cut AI costs by 87% playbook.
- **products/git-workflow-ai/** — Version control for AI workspaces.
- **products/self-improvement-100x-loop/** — Error once, improve forever.
- **products/karpathy-agent-os-starter-kit/** — Installable AI discipline (early access).

- **docs/gold-nuggets/GOLD_AI_EMPIRE_SHIPPING_MANIFEST_2026-06-29.md** — Ship everything / monetize everything manifest.
- **products/one-person-ai-agent-company/go-to-market/execution/DASHBOARD.md** — Active shipping sprint dashboard.
- **products/one-person-ai-agent-company/go-to-market/** — 14-day launch plan, cold outreach templates, lead magnet plan.
- **products/one-person-ai-agent-company/** — Productized landing page, pricing, sales copy for the viral One-Person AI Agent Company template.

- **skills/orchestration/git-workflow-ai/** — Git workflow for AI workspaces (three repos, daily rhythm, rollback/prune/eval versioning).


- **docs/gold-nuggets/** — AI Empire Gold Nuggets from this session.
- **docs/AI_EMPIRE_INSIGHTS_2026-06-29.md** — Integration summary.
- **templates/one-person-ai-agent-company/** — Solo AI agent company starter.
- **skills/orchestration/swarm-fan-out/** — Hermes multi-subagent orchestration skill.
- **control-plane/hermes/config/model-policy.env.template** — Chinese-stack task routing template.

See the insights doc for the full list of next steps.


Consolidated system from Hermes Core Extract + Archimedes Core Extract.

## Structure

```
hermes-archi/
├── control-plane/      # Agent runtimes: Hermes, Jarvis, Harvey, OpenClaw
│   ├── hermes/         # Router, Goals, Verifier, Knowledge Graph
│   ├── jarvis/         # Intent classification, Memory, Obsidian export
│   ├── harvey/         # Legal runtime, Stripe bridge
│   ├── openclaw/       # Skills engine, Execution policy
│   ├── common/         # Shared: Bus client, Models, Ollama wrapper
│   ├── scripts/        # deploy, health, start/stop
│   └── tests/          # Unit + E2E
├── model-layer/        # Model rotation + tool detection (TypeScript)
│   ├── orchestrator.ts # Multi-model orchestration
│   ├── model_server.ts # Model serving layer
│   ├── memory.ts       # Memory management
│   └── explorers/      # Web, integration, memory explorers
├── telegram/           # Telegram bot + agent departments + queue
│   ├── telegram-bot/   # Bot handlers (commands, X analysis, tasks)
│   ├── agents/         # Department agents (engineering, marketing, research, X)
│   ├── queue/          # Background worker
│   └── x-analyzer/     # X/Twitter scraper + analyzer
├── trading/            # QPTS / Polymarket trading module
├── gpe-core/           # GPE task dispatcher
├── integrations/       # External integrations (Telegram bot.ts)
├── legacy/             # Galaxia legacy (friends configs)
└── audit/              # Consolidation reports
```

## Origin

| Source | Files | LOC | Contribution |
|--------|-------|-----|-------------|
| hermes-core-extract | 50 | 6,789 | Model rotation, tool detection, Telegram agents |
| archimedes-core-extract | 114 | 11,708 | Control plane (Core4), QPTS trading, GPE |

## Stack

- **Control Plane**: Python (FastAPI-style runtimes)
- **Model Layer**: TypeScript (orchestrator, explorers)
- **Telegram**: Python (bot, agents, queue workers)
- **Infra**: Docker Compose, shell scripts
