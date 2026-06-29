#!/bin/zsh
# CTO Agent — tech health
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/cto/outputs
mkdir -p $OUT
cd ~/ai-empire/projects/hermes-archi || exit 1
{
  echo "# Tech Health Report — $DATE"
  echo ""
  echo "## Git Status"
  git status --short
  echo ""
  echo "## Disk Space"
  df -h ~ | tail -1
  echo ""
  echo "## Recent Commits"
  git log --oneline -5
} > $OUT/tech_health_$DATE.md
