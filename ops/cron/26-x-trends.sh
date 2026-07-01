#!/bin/bash
# Silver Loop: X Trends Ingest (HIL-protected)
# Pulls real-time X/Twitter signal via X MCP (or Kimi/Ollama/Mock fallback) daily.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
mkdir -p "$REPO/state/x"
cd "$REPO"
source .venv/bin/activate

# HIL Gate: GREEN — read-only research, local state only
python3 control-plane/hermes/hil_loop_enforcer.py \
  "26-x-trends" \
  "Lese X/Twitter Trends zu AI-Agent-Themen ein und speichere sie lokal als JSON" \
  -- python3 agents/research/x_trends.py
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
ops/cron/26-x-trends.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
