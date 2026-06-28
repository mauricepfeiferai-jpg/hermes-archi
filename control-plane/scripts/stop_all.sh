#!/usr/bin/env bash
# Pfeifer Core4 — stop all locally-started daemons.

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT/run"

for name in jarvis harvey openclaw hermes; do
    pidf="$RUN_DIR/${name}.pid"
    if [ -f "$pidf" ]; then
        pid="$(cat "$pidf")"
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" && echo "[$name] stopped (pid $pid)"
        else
            echo "[$name] not running"
        fi
        rm -f "$pidf"
    else
        echo "[$name] no pid file"
    fi
done
