#!/usr/bin/env bash
# Pfeifer Core4 — start all daemons locally for development.
# Usage:  ./scripts/start_all.sh
#         Logs go to ./run/*.log; PIDs to ./run/*.pid

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT/run"
mkdir -p "$RUN_DIR"

cd "$ROOT"  # control-plane/ — so each script can resolve its imports

[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a

PYTHON="${PYTHON_BIN:-python3}"

start_one() {
    local name="$1"
    local script="$2"
    local logf="$RUN_DIR/${name}.log"
    local pidf="$RUN_DIR/${name}.pid"

    if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then
        echo "[$name] already running (pid $(cat "$pidf"))"
        return
    fi

    echo "[$name] starting ..."
    nohup "$PYTHON" "$script" >"$logf" 2>&1 &
    echo $! >"$pidf"
    sleep 0.3
    echo "[$name] pid $(cat "$pidf") — log: $logf"
}

# Order matters: Hermes first, then everyone else registers with it.
start_one "hermes"   "$ROOT/hermes/runtime/main.py"
sleep 1
start_one "openclaw" "$ROOT/openclaw/runtime/main.py"
start_one "harvey"   "$ROOT/harvey/runtime/main.py"
start_one "jarvis"   "$ROOT/jarvis/runtime/main.py"

sleep 2
echo
echo "--- Health check ---"
exec "$ROOT/scripts/health.sh"
