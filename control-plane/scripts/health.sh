#!/usr/bin/env bash
# Health check all 4 daemons.

# Load .env so ports match the running daemons (e.g. isolated 188xx range).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a

PORTS=(
    "hermes:${HERMES_PORT:-18790}"
    "jarvis:${JARVIS_PORT:-18791}"
    "openclaw:${OPENCLAW_PORT:-18789}"
    "harvey:${HARVEY_PORT:-18792}"
)

EXIT_CODE=0
for spec in "${PORTS[@]}"; do
    name="${spec%%:*}"
    port="${spec##*:}"
    url="http://127.0.0.1:${port}/health"
    body="$(curl -fsS --max-time 3 "$url" 2>/dev/null || true)"
    if [ -z "$body" ]; then
        printf "%-10s ❌ down (port %s)\n" "$name" "$port"
        EXIT_CODE=1
    else
        uptime="$(printf '%s' "$body" | grep -oE '"uptime_seconds":[0-9]+' | head -1 | grep -oE '[0-9]+')"
        printf "%-10s ✅ ok    (port %s, uptime ${uptime:-?}s)\n" "$name" "$port"
    fi
done

exit "$EXIT_CODE"
