#!/bin/zsh
# Sales Agent — inbox + pipeline
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/sales/outputs
mkdir -p $OUT $ROOT/sales/inbox
python3 $ROOT/ops/cron/run_agent.py sales inbox --date $DATE --out $OUT/pipeline_$DATE.md
