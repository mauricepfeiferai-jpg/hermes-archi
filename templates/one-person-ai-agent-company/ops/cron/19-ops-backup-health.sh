#!/bin/zsh
# Ops Agent — backup + health
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/ops/outputs
mkdir -p $OUT ~/ai-empire/backups
BACKUP=~/ai-empire/backups/ai-empire-$(date +%Y%m%d-%H%M%S).tar.gz
{
  echo "# Ops Health Report — $DATE"
  echo ""
  echo "## Backup"
  echo "Target: $BACKUP"
  tar -czf "$BACKUP" -C ~ ai-empire/projects/hermes-archi 2>&1 | tail -5
  gzip -t "$BACKUP" && echo "Backup integrity: OK" || echo "Backup integrity: FAIL"
  echo ""
  echo "## Disk Space"
  df -h ~ | tail -1
  echo ""
  echo "## Cron Status"
  crontab -l 2>/dev/null | grep ai-agent-company || echo "No crontab entries found"
} > $OUT/health_$DATE.md
