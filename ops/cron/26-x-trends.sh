#!/bin/bash
# Silver Loop: X Trends Ingest
# Pulls real-time X/Twitter signal via X MCP (or Kimi fallback) daily.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
mkdir -p "$REPO/state/x"
cd "$REPO"
python3 agents/research/x_trends.py
