#!/bin/zsh
# Engineer Agent — pick next backlog task, ship it
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
mkdir -p $ROOT/engineer/{backlog,done,outputs}
python3 $ROOT/ops/cron/run_agent.py engineer ship-next --date $DATE --out $ROOT/engineer/outputs/daily_ship_$DATE.md
