#!/bin/zsh
# Researcher Agent — daily scan
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/researcher/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py researcher scan --date $DATE --out $OUT/daily_brief_$DATE.md
