#!/bin/bash
# Silver Loop: X Trends Ingest (HIL-protected)
# Pulls real-time X/Twitter signal via X MCP (or Kimi/Ollama/Mock fallback) daily.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
mkdir -p "$REPO/state/x"
cd "$REPO"

# HIL Gate: GREEN — read-only research, local state only
python3 control-plane/hermes/hil_loop_enforcer.py \
  "26-x-trends" \
  "Lese X/Twitter Trends zu AI-Agent-Themen ein und speichere sie lokal als JSON" \
  -- python3 agents/research/x_trends.py
