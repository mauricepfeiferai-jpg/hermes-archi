# Hermes-Archi

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
