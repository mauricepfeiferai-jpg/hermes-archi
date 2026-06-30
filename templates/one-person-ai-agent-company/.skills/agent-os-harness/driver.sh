#!/bin/bash
set -euo pipefail
TASK="${1:-list agents}"
cd "$HOME/ai-empire/projects/hermes-archi" || exit 1
python3 agents/agent-os-harness/dispatch.py emperor "$TASK"
