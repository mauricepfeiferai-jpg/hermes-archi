#!/bin/zsh
# Run today's morning action queue
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DATE=$(date +%Y-%m-%d)
QUEUE_MD="$ROOT/ceo/outputs/morning_queue_$DATE.md"
QUEUE_JSON="$ROOT/../../state/ceo/morning_queue_$DATE.json"
OUT="$ROOT/ops/outputs/queue_status_$DATE.md"

mkdir -p "$ROOT/ops/outputs"
{
  echo "# Morning Queue Status — $DATE"
  echo ""

  QUEUE_SOURCE=""
  if [ -f "$QUEUE_MD" ]; then
    QUEUE_SOURCE="$QUEUE_MD"
  elif [ -f "$QUEUE_JSON" ]; then
    QUEUE_SOURCE="$QUEUE_JSON"
  fi

  if [ -z "$QUEUE_SOURCE" ]; then
    echo "⚠️ Morning queue not found."
    echo "Run: bash ops/cron/06-ceo-daily-goals.sh"
    exit 1
  fi

  echo "Queue source: $QUEUE_SOURCE"
  echo ""
  echo "## Queue Contents"
  if [[ "$QUEUE_SOURCE" == *.md ]]; then
    cat "$QUEUE_SOURCE"
  else
    python3 -c "import json; d=json.load(open('$QUEUE_SOURCE')); [print(f'- {p[\"rank\"]}. {p[\"action\"]} ({p[\"owner\"]}) — impact: {p[\"impact\"]}') for p in d.get('priorities', [])]"
  fi
  echo ""
  echo "## Execution Log"
  echo "- [x] Queue loaded"
  echo "- [ ] Items need agent execution (bridge integration pending)"
  echo ""
  echo "## Definition of Done"
  echo "- [ ] All queue items executed or skipped with reason"
  echo "- [ ] Output files verified"
  echo "- [ ] Errors logged"
} > "$OUT"

echo "Wrote: $OUT"
