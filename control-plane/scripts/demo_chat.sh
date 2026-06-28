#!/usr/bin/env bash
# Quick smoke-test: send a chat to Jarvis end-to-end.

set -euo pipefail

JARVIS_URL="${JARVIS_URL:-http://127.0.0.1:18791}"
TEXT="${1:-Hi Jarvis, was läuft?}"

echo "→ POST $JARVIS_URL/chat"
echo "  text: $TEXT"
echo
curl -sS -X POST "$JARVIS_URL/chat" \
    -H "Content-Type: application/json" \
    -d "$(python -c "import json,sys; print(json.dumps({'text': sys.argv[1], 'user_id': 'maurice'}))" "$TEXT")"
echo
