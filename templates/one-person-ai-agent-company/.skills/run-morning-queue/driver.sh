#!/bin/zsh
# Run today's morning action queue
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DATE=$(date +%Y-%m-%d)
QUEUE="$ROOT/ceo/outputs/morning_queue_$DATE.md"
OUT="$ROOT/ops/outputs/queue_status_$DATE.md"

mkdir -p "$ROOT/ops/outputs"
{
  echo "# Morning Queue Status — $DATE"
  echo ""
  if [ ! -f "$QUEUE" ]; then
    echo "⚠️ Morning queue not found: $QUEUE"
    echo "Run: bash ops/cron/06-ceo-daily-goals.sh"
    exit 1
  fi
  echo "Queue file: $QUEUE"
  echo ""
  echo "## Execution Log"
  # Stub: in production, parse the queue table and run each command
  echo "- [x] CEO daily goals (ran)"
  echo "- [ ] CTO tech health (stub)"
  echo "- [ ] Engineer ship (stub)"
  echo ""
  echo "## Definition of Done"
  echo "- [ ] All queue items executed or skipped with reason"
  echo "- [ ] Output files verified"
  echo "- [ ] Errors logged"
} > "$OUT"

echo "Wrote: $OUT"
