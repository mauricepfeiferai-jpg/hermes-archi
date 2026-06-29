#!/bin/zsh
# Manual loop runner — execute all daily reviews and retro
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
WEEK=$(date +%Y-W%V)

mkdir -p $ROOT/loop/outputs
bash $ROOT/ops/cron/20-loop-review.sh
bash $ROOT/ops/cron/21-loop-improve.sh

# Weekly retro on Sundays
if [ "$(date +%u)" = "7" ]; then
  cat $ROOT/loop/RETRO_TEMPLATE.md | sed "s/YYYY-Www/$WEEK/g" > $ROOT/loop/outputs/retro_$WEEK.md
  echo "Weekly retro started: $ROOT/loop/outputs/retro_$WEEK.md"
fi
