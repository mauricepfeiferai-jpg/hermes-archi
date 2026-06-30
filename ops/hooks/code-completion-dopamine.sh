#!/bin/bash
# Hook: emit dopamine reward after meaningful code completion
# Usage: source this script after a successful build/test/commit
REPO="$HOME/ai-empire/projects/hermes-archi"
FILES=${1:-0}
TESTS=${2:-0}
COMMITS=${3:-0}
python3 "$REPO/agents/agent-os-harness/live_dopamine.py" code.completed "{\"files\": $FILES, \"tests_passed\": $TESTS, \"commits\": $COMMITS}"
