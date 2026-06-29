# Test Report — One-Person AI Agent Company Template

**Date:** 2026-06-29
**Tester:** Hermes / automated smoke test
**Status:** ✅ PASS (stub mode)

## Test Scope
- 7 agent roles: job descriptions complete
- 10 cron scripts: executable and produce outputs
- Loop runner: review + retro + patch proposal
- Crontab: syntax valid, loads 10 entries
- Dispatcher: stub mode default, Hermes opt-in
- Deliverable zip: clean, outputs excluded
- Landing page + OG image: live and reachable

## Test Environment
- macOS, zsh
- Python 3.14.5
- Hermes CLI installed but NOT enabled for test
- Netlify CLI authenticated

## Test Results

| Test | Result | Notes |
|---|---|---|
| `06-ceo-daily-goals.sh` | ✅ PASS | Output: `ceo/outputs/daily_goals_YYYY-MM-DD.md` |
| `07-cto-tech-health.sh` | ✅ PASS | Git + disk + recent commits reported |
| `08-engineer-ship.sh` | ✅ PASS | Output: `engineer/outputs/daily_ship_*.md` |
| `09-researcher-scan.sh` | ✅ PASS | Output: `researcher/outputs/daily_brief_*.md` |
| `10-writer-content.sh` | ✅ PASS | Output: `writer/outputs/daily_content_*.md` |
| `11-sales-inbox.sh` | ✅ PASS | Output: `sales/outputs/pipeline_*.md` |
| `12-sales-outbound.sh` | ✅ PASS | Output: `sales/outputs/outbound_draft_*.md` |
| `19-ops-backup-health.sh` | ✅ PASS | Backup archive created + integrity checked |
| `20-loop-review.sh` | ✅ PASS | Output: `loop/outputs/daily_review_*.md` |
| `21-loop-improve.sh` | ✅ PASS | Output: `loop/outputs/patch_proposal_*.md` |
| `loop/run_loop.sh` | ✅ PASS | Runs review + improve |
| Crontab syntax | ✅ PASS | 10 entries loaded successfully, then cleared |
| Shell syntax | ✅ PASS | All `.sh` files pass `bash -n` |
| Python syntax | ✅ PASS | `ops/cron/run_agent.py` passes `py_compile` |
| JSON validity | ✅ PASS | `loop/lessons.json` valid |
| Deliverable zip | ✅ PASS | 26KB, 67 files, no outputs included |
| Landing page HTTP | ✅ PASS | `200` for index and product page |
| OG image HTTP | ✅ PASS | `200` for `assets/og-image.png` |

## Known Issues

| Issue | Severity | Note |
|---|---|---|
| Hermes CLI dispatch hangs / returns no output in non-interactive mode | 🟡 MEDIUM | Default is stub mode. Hermes mode is opt-in via `HERMES_USE=1`. Documented in README. |
| Output files are stubs, not real agent-generated content | 🟢 EXPECTED | Stub mode is intentional for safe testing and cost control. |
| No real RSS/web sources configured for researcher | 🟢 EXPECTED | Buyer must add `researcher/sources.json` or replace stub. |
| No real CRM JSON for sales | 🟢 EXPECTED | Buyer must create `sales/crm.json`. |
| Backup script uses local tar only (no cloud) | 🟡 LOW | Documented. Buyer can replace with rsync/S3. |

## Files Checked

- `ceo/JOB_DESCRIPTION.md`
- `cto/JOB_DESCRIPTION.md`
- `engineer/JOB_DESCRIPTION.md`
- `researcher/JOB_DESCRIPTION.md`
- `writer/JOB_DESCRIPTION.md`
- `sales/JOB_DESCRIPTION.md`
- `ops/JOB_DESCRIPTION.md`
- `loop/JOB_DESCRIPTION.md`
- `ops/cron/06-ceo-daily-goals.sh`
- `ops/cron/07-cto-tech-health.sh`
- `ops/cron/08-engineer-ship.sh`
- `ops/cron/09-researcher-scan.sh`
- `ops/cron/10-writer-content.sh`
- `ops/cron/11-sales-inbox.sh`
- `ops/cron/12-sales-outbound.sh`
- `ops/cron/19-ops-backup-health.sh`
- `ops/cron/20-loop-review.sh`
- `ops/cron/21-loop-improve.sh`
- `ops/cron/run_agent.py`
- `ops/cron/crontab.txt`
- `loop/run_loop.sh`
- `loop/REVIEW_TEMPLATE.md`
- `loop/RETRO_TEMPLATE.md`
- `loop/lessons.json`
- `README.md`
- `variants/bma-service-company/README.md`

## Go-Live Readiness

**READY FOR SALE AS A TEMPLATE.**

The system is runnable out of the box in stub mode and can be upgraded to real Hermes dispatch by setting `HERMES_USE=1`. It is not a fully autonomous AI company yet, but it is a complete operating system scaffold with executable workflows.

## Recommended First Use

1. Copy template to buyer's machine.
2. Run one manual cycle: `bash ops/cron/06-ceo-daily-goals.sh` ... `bash loop/run_loop.sh`.
3. Review outputs in `*/outputs/`.
4. Customize job descriptions and add real inputs (CRM, sources, backlog).
5. Enable Hermes mode only after verifying cost and model config.
6. Install crontab when ready: `cat ops/cron/crontab.txt | crontab -`.

## Next Improvements (post-launch)

- Add real Hermes/Claude dispatch with timeout and output parsing
- Add `researcher/sources.json` example with 3 real feeds
- Add `sales/crm.json` example
- Add dashboard script that aggregates all outputs
- Add cloud backup option (rsync/S3)
