#!/bin/zsh
# Spec Agent — writes PRODUCT.md + TECH.md for a task
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
TASK_ID="${1:-unknown-task}"
OUT_DIR=$ROOT/specs/$TASK_ID
mkdir -p $OUT_DIR

python3 $ROOT/ops/cron/run_agent.py spec_agent write-spec \
  --date $DATE \
  --out $ROOT/spec_agent/outputs/spec_status_$DATE.md \
  --task-id $TASK_ID

# Copy templates into spec dir if not present
[ -f "$OUT_DIR/PRODUCT.md" ] || cp $ROOT/spec_agent/spec_template_PRODUCT.md $OUT_DIR/PRODUCT.md
[ -f "$OUT_DIR/TECH.md" ] || cp $ROOT/spec_agent/spec_template_TECH.md $OUT_DIR/TECH.md

echo "Spec written to $OUT_DIR"
