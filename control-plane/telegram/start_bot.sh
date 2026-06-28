#!/usr/bin/env bash
# Start the Core4 Telegram bot (topic-routing mode)
# Usage: ./start_bot.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BOT_DIR="$REPO_ROOT/integrations/telegram"
RUN_DIR="$REPO_ROOT/control-plane/run"

mkdir -p "$RUN_DIR"

# Ensure .env exists
if [[ ! -f "$BOT_DIR/.env" ]]; then
  echo "ERROR: $BOT_DIR/.env not found."
  echo "Copy from: $SCRIPT_DIR/.env.example"
  exit 1
fi

# Kill existing bot process if running
PID_FILE="$RUN_DIR/telegram.pid"
if [[ -f "$PID_FILE" ]]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Stopping existing bot (PID $OLD_PID)..."
    kill "$OLD_PID"
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

cd "$BOT_DIR"

# Ensure dependencies are installed
if [[ ! -d node_modules ]]; then
  echo "Installing npm dependencies..."
  npm install --prefer-offline 2>/dev/null || npm install
fi

echo "Starting Core4 Telegram Bot..."
nohup npx tsx src/bot.ts >> "$RUN_DIR/telegram.log" 2>&1 &
BOT_PID=$!
echo "$BOT_PID" > "$PID_FILE"

echo "Bot started (PID $BOT_PID)"
echo "Logs: $RUN_DIR/telegram.log"
echo "PID:  $PID_FILE"
