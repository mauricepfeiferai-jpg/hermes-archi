#!/bin/zsh
# Writer Agent — content draft
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/writer/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py writer draft --date $DATE --out $OUT/daily_content_$DATE.md
