# Cron Jobs — One-Person AI Agent Company

## Silver Loops (Agent OS)

| Time | Script | Agent | Purpose |
|---|---|---|---|
| 06:00 | `06-ceo-daily-goals.sh` | CEO | Morning queue |
| 06:15 | `07-cto-tech-health.sh` | CTO | System health |
| 07:00 | `08-engineer-ship.sh` | Engineer | Ship backlog |
| 08:00 | `22-research-ingestion.sh` | Researcher | Discover AI repos/papers |
| 08:30 | `23-library-sync.sh` | CTO | Sync indices |
| 09:00 | `24-dopamine-score.sh` | Loop | Score yesterday's dopamine |
| 09:15 | `25-neural-broadcast.sh` | Emperor | Broadcast state everywhere |
| 18:00 | `19-ops-backup-health.sh` | Ops | Backup + integrity |
| 20:00 | `20-loop-review.sh` | Loop | Daily retro |
| 20:30 | `21-loop-improve.sh` | Loop | Patch system |

## Install

```bash
cat ops/cron/crontab.txt | crontab -
```

## Agent OS Files

- `agents/agent-os-harness/agent_registry.json`
- `agents/agent-os-harness/dispatch.py`
- `agents/agent-os-harness/silver_loop_harness.py`
- `state/neural-bus/`
- `state/dopamine/`
- `state/libraries/`
