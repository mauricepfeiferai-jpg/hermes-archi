#!/bin/bash
# Silver Loop: Dopamine Scoring
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
cd "$REPO"
python3 agents/agent-os-harness/dopamine_scorer.py "$REPO" "$YESTERDAY" "$DATE"
