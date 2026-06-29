#!/bin/zsh
DATE="${1:-$(date +%Y-%m-%d)}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
bash "$ROOT/ops/cron/10-writer-content.sh"
