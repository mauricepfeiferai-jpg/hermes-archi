#!/bin/zsh
# Loop Agent — daily review
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/loop/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py loop review --date $DATE --out $OUT/daily_review_$DATE.md
