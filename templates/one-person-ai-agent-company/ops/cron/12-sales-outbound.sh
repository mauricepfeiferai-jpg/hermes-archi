#!/bin/zsh
# Sales Agent — outbound draft
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/sales/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py sales outbound --date $DATE --out $OUT/outbound_draft_$DATE.md
