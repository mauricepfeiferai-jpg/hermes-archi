# One-Person AI Agent Company Template

Run a company with 7 AI agents, 10 cron jobs, and 0 employees.

## Structure

```
ai-company/
├── ceo/            # Direction, priorities, decisions
├── cto/            # Tech health, architecture, upgrades
├── engineer/       # Ship backlog items with tests
├── researcher/     # Market scan + daily brief
├── writer/         # Content engine
├── sales/          # Pipeline + outbound
├── ops/            # Backups, cron, system health
└── loop/           # Review / retro / self-improve
```

## Quick Start

1. Copy this folder into your project:
   ```bash
   cp -R one-person-ai-agent-company ~/my-ai-company/
   cd ~/my-ai-company
   ```

2. Install the crontab:
   ```bash
   cat ops/cron/crontab.txt | crontab -
   ```

3. Run one manual cycle to verify:
   ```bash
   bash ops/cron/06-ceo-daily-goals.sh
   bash ops/cron/07-cto-tech-health.sh
   bash ops/cron/08-engineer-ship.sh
   bash ops/cron/09-researcher-scan.sh
   bash ops/cron/10-writer-content.sh
   bash ops/cron/11-sales-inbox.sh
   bash ops/cron/12-sales-outbound.sh
   bash ops/cron/19-ops-backup-health.sh
   bash loop/run_loop.sh
   ```

4. Review outputs in `*/outputs/`.

## Default Schedule

| Time | Agent | Job |
|---|---|---|
| 06:00 | CEO | Daily goals |
| 06:15 | CTO | Tech health |
| 07:00 | Engineer | Ship backlog |
| 08:00 | Researcher | Trend scan |
| 09:00 | Writer | Content draft |
| 10:00 | Sales | Lead inbox |
| 11:00 | Sales | Outbound draft |
| 18:00 | Ops | Backup + health |
| 20:00 | Loop | Daily review |
| 20:30 | Loop | Self-improve |

## Replace the Stub Runner

`ops/cron/run_agent.py` is a placeholder. Connect it to:
- Hermes CLI / Hermes runtime API
- OpenClaw MCP dispatch
- Claude Code non-interactive mode
- Kimi / OpenAI / local model endpoints

## Approval Gate

Any destructive or production action must write to `*/outputs/approval_needed_*.md`. Window 1 / human reviews before execution.

## BMA Service Business Variant

See `variants/bma-service-company/` for roles adapted to German fire-safety contractors: project manager, compliance officer, field engineer, customer success.

## Hermes Wiring

The template includes a dispatcher script at `ops/cron/run_agent.py`.

By default it writes a structured stub output so you can test the system immediately without spending API credits.

To enable real Hermes dispatch:

```bash
export HERMES_PATH=/Users/maurice/.local/bin/hermes
bash ops/cron/10-writer-content.sh
```

Each cron script passes the agent role, task, date, and output path to `run_agent.py`. The dispatcher calls:

```bash
hermes --yolo --safe-mode -z "<prompt with full context>"
```

If Hermes is unavailable or slow, the dispatcher falls back to the stub.

## Cost Control

- Stub mode: free, runs instantly, good for testing the loop
- Hermes mode: uses your configured model; run one script manually before enabling all 10 cron jobs
- Recommended: keep 06:00–20:30 schedule, review first week of real outputs before scaling
