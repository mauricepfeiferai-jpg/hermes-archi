#!/bin/zsh
# Triage Agent — labels incoming issue or task
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
TASK_ID="${1:-unknown-task}"
mkdir -p $ROOT/triage_agent/outputs

python3 $ROOT/ops/cron/run_agent.py triage_agent triage \
  --date $DATE \
  --out $ROOT/triage_agent/outputs/triage_$TASK_ID_$DATE.md \
  --task-id $TASK_ID

echo "Triage complete. Label manually or via GitHub Action based on output."
