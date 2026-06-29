#!/bin/zsh
AGENT="${1:-ceo}"
TASK="${2:-daily-goals}"
DATE="${3:-$(date +%Y-%m-%d)}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

OUT_DIR="$ROOT/$AGENT/outputs"
mkdir -p "$OUT_DIR"

python3 "$ROOT/ops/cron/run_agent.py" "$AGENT" "$TASK" --date "$DATE" --out "$OUT_DIR/${TASK}_${DATE}.md"
