# Morning Action Queue — YYYY-MM-DD

## Executive Summary
- Top priority today:
- Revenue risk:
- Ship risk:
- Human decision needed:

## Ranked Actions

| Rank | Time | Agent | Action | Skill/Script | Input | Output | Urgency |
|---|---|---|---|---|---|---|---|
| 1 | 06:00 | CTO | Tech health check | `ops/cron/07-cto-tech-health.sh` | git, disk, backups | `cto/outputs/tech_health_*.md` | High |
| 2 | 06:15 | CEO | Set daily goals + queue | `ops/cron/06-ceo-daily-goals.sh` | all outputs | `ceo/outputs/morning_queue_*.md` | High |
| 3 | 07:00 | Engineer | Ship next backlog item | `ops/cron/08-engineer-ship.sh` | backlog + goals | `engineer/outputs/daily_ship_*.md` | Medium |
| 4 | 08:00 | Researcher | Market scan | `ops/cron/09-researcher-scan.sh` | sources | `researcher/outputs/daily_brief_*.md` | Medium |
| 5 | 09:00 | Writer | Content draft | `ops/cron/10-writer-content.sh` | brief + goals | `writer/outputs/daily_content_*.md` | Medium |
| 6 | 10:00 | Sales | Lead inbox triage | `ops/cron/11-sales-inbox.sh` | crm + inbox | `sales/outputs/pipeline_*.md` | High |
| 7 | 11:00 | Sales | Outbound draft | `ops/cron/12-sales-outbound.sh` | brief + crm | `sales/outputs/outbound_draft_*.md` | Medium |
| 8 | 18:00 | Ops | Backup + health | `ops/cron/19-ops-backup-health.sh` | repos, cron | `ops/outputs/health_*.md` | High |
| 9 | 20:00 | Loop | Daily review | `ops/cron/20-loop-review.sh` | all outputs | `loop/outputs/daily_review_*.md` | High |
| 10 | 20:30 | Loop | Self-improve | `ops/cron/21-loop-improve.sh` | review | `loop/outputs/patch_proposal_*.md` | High |

## Human Approval Needed
- [ ] 

## Notes
-
