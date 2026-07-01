#!/bin/bash
# Serve dashboard over local HTTP so fetch('data.json') works fresh
PORT="${1:-8080}"
echo "Serving dashboard at http://localhost:$PORT"
echo "Press Ctrl+C to stop"
cd "$(dirname "$0")"
python3 -m http.server "$PORT"
