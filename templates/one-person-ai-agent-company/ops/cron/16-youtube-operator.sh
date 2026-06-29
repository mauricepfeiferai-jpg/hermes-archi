#!/bin/zsh
# YouTube Operator Agent — weekly content + analytics review
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/youtube_operator/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py youtube_operator weekly \
  --date $DATE --out $OUT/content_calendar_$DATE.md
