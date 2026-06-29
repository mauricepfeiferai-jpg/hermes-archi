#!/bin/zsh
# CEO Agent — daily goals
source ~/.openclaw/.env 2>/dev/null || true
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/ceo/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py ceo daily-goals --date $DATE --out $OUT/daily_goals_$DATE.md
