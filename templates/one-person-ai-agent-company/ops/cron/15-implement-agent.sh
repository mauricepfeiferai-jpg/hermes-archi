#!/bin/zsh
# Implementation Agent — implements a ready-to-implement task
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
TASK_ID="${1:-unknown-task}"
mkdir -p $ROOT/engineer/done

if [ -d "$ROOT/specs/$TASK_ID" ]; then
  echo "Found spec for $TASK_ID. Implementing according to spec."
else
  echo "No spec found. One-shot implementation."
fi

python3 $ROOT/ops/cron/run_agent.py engineer implement \
  --date $DATE \
  --out $ROOT/engineer/outputs/daily_ship_$DATE.md \
  --task-id $TASK_ID

echo "Implementation attempt complete."
