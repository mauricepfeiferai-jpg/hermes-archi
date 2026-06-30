# One-Person AI Agent Company Template

Run a company with 7 AI agents, 10 cron jobs, and 0 employees.

## The Real Product: The Morning Queue

The hardest problem is not building skills. It is getting the person who isn't AI-native to run the right skill at the right moment.

This template solves that with a **morning action queue**: every day the CEO Agent ranks what matters, then routes each agent to the exact skill/script they should run. You open the dashboard and work the queue.

## Dashboard

Open `dashboard/index.html` in your browser to see the live status of your agent company.

Run `python3 dashboard/generate_data.py` after a cron cycle to populate real output data.

![Dashboard Preview](dashboard/dashboard-preview.png)

## Structure

```
ai-company/
├── ceo/               # Direction + morning action queue
├── cto/               # Tech health
├── engineer/          # Ship backlog
├── researcher/        # Market scan
├── writer/            # Content engine
├── sales/             # Pipeline + outbound
├── ops/               # Backups, cron, system health
├── loop/              # Review / retro / self-improve
├── spec_agent/        # Specs for complex tasks
├── youtube_operator/  # YouTube channel operating system
└── dashboard/         # Visual status UI
```

## Quick Start

1. Copy this folder into your project:
   ```bash
   cp -R one-person-ai-agent-company ~/my-ai-company/
   cd ~/my-ai-company
   ```

2. Run one manual cycle to verify:
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

3. Generate dashboard data:
   ```bash
   python3 dashboard/generate_data.py
   open dashboard/index.html
   ```

4. Install the crontab when ready:
   ```bash
   cat ops/cron/crontab.txt | crontab -
   ```

5. Review the morning queue in `ceo/outputs/morning_queue_YYYY-MM-DD.md`.

## Default Schedule

| Time | Agent | Job |
|---|---|---|
| 06:00 | CEO | Daily goals + morning queue |
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

Enable real dispatch:
```bash
export HERMES_USE=1
bash ops/cron/10-writer-content.sh
```

## Approval Gate

Any destructive or production action must write to `*/outputs/approval_needed_*.md`. Window 1 / human reviews before execution.

## Variants

- **BMA Service Business** — `variants/bma-service-company/` for German fire-safety contractors
- **Cloud Software Factory** — `github-actions/` for Triage → Spec → Implement on GitHub

## Cost Control

- Stub mode: free, runs instantly, good for testing the loop
- Hermes mode: uses your configured model; run one script manually before enabling all 10 cron jobs
- Recommended: keep 06:00–20:30 schedule, review first week of real outputs before scaling

## The 4 Loops That Make It Work

This template implements the four loops that senior Claude Code users run:

1. **Edit/Test Loop** — every change verified by a hook or check (`ops/cron/run_agent.py`, scripts pass `bash -n`, Python passes `py_compile`)
2. **Goal Loop** — CEO Agent sets daily goals and the system works until outputs exist
3. **Verification Loop** — multiple agents review each other's outputs before finalization
4. **Memory Loop** — daily review + retro writes lessons into `loop/lessons.json` and updates rules

Running all four is what separates hobbyists from operators.

## Agent OS Mode (NEW)

This template now includes an **Agent OS Harness** that connects every agent like neurons:

- **Neural Bus**: `state/neural-bus/` — all events flow as JSON
- **Dopamine Scoring**: `state/dopamine/score.json` — completed code releases reward
- **Silver Loops**: fixed reflex loops in `ops/cron/22-25*.sh`
- **Agent Registry**: `agents/agent-os-harness/agent_registry.json` — Hermes, OpenClaw, Claude, Codex, Kimi, Ollama
- **Dispatch Router**: `agents/agent-os-harness/dispatch.py` — route task to the right runtime
- **OpenClaw Bridge**: `integrations/openclaw/MCP_BRIDGE.md`

### Silver Loops Added

| Time | Loop | Purpose |
|---|---|---|
| 08:00 | Research Ingest | Discover AI repos/papers/tools daily |
| 08:30 | Library Sync | Rebuild skill/repo/knowledge indices |
| 09:00 | Dopamine Score | Score yesterday's completed work |
| 09:15 | Neural Broadcast | Push state to OpenClaw, dashboard, memory |

### Dopamine Rule

When an agent completes code:

```bash
python3 -c "from agents.agent_os_harness.dispatch import update_dopamine; update_dopamine('code.completed', {'files':3, 'tests_passed':5, 'commits':1})"
```

The score decays daily by 5% (forgetting curve). Shipping streaks increase the multiplier.
