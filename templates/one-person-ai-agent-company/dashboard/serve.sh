#!/bin/bash
# Serve dashboard over local HTTP so fetch('data.json') works fresh
PORT="${1:-8080}"
cd "$(dirname "$0")" || exit 1

# Find free port if 8080 is taken
for p in $(seq "$PORT" 8099); do
  if ! curl -s --max-time 1 "http://127.0.0.1:$p/" >/dev/null 2>&1; then
    PORT=$p
    break
  fi
done

echo "Serving dashboard at http://localhost:$PORT"
echo "Press Ctrl+C to stop"
python3 -m http.server "$PORT"
