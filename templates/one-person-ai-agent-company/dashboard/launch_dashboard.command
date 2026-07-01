#!/bin/bash
# One-click launcher for AI Agent Company Dashboard
DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8777
PIDFILE="$DIR/.dashboard-server.pid"

# Kill old server if running
if [ -f "$PIDFILE" ]; then
  OLD_PID=$(cat "$PIDFILE" 2>/dev/null)
  if [ -n "$OLD_PID" ]; then
    kill "$OLD_PID" 2>/dev/null || true
    sleep 0.5
  fi
  rm -f "$PIDFILE"
fi

# Find free port starting from 8777
for p in $(seq 8777 8799); do
  if ! curl -s --max-time 1 http://127.0.0.1:$p/ >/dev/null 2>&1; then
    PORT=$p
    break
  fi
done

# Start server
cd "$DIR" || exit 1
nohup python3 -m http.server $PORT > /tmp/dashboard-server-$PORT.log 2>&1 </dev/null &
echo $! > "$PIDFILE"
disown 2>/dev/null || true

# Wait for server to be ready
for i in $(seq 1 20); do
  if curl -s --max-time 1 http://127.0.0.1:$PORT/ >/dev/null 2>&1; then
    echo "Dashboard running at http://127.0.0.1:$PORT"
    open "http://127.0.0.1:$PORT"
    exit 0
  fi
  sleep 0.2
done

echo "Server failed to start. Check /tmp/dashboard-server-$PORT.log"
cat /tmp/dashboard-server-$PORT.log 2>/dev/null
exit 1
