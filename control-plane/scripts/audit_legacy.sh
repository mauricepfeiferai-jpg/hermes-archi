#!/usr/bin/env bash
# Core4 ↔ Legacy overlap audit (read-only, safe).
#
# Maps the existing agent/orchestration services on this host against the new
# Core4 stack so we can decide what stays long-term. Touches nothing — pure
# inspection. Trading/data services are intentionally out of scope.
#
# Run:  bash control-plane/scripts/audit_legacy.sh
#       (or pipe to a file:  ... | tee /tmp/core4_audit.txt)

set -uo pipefail

line() { printf '%s\n' "────────────────────────────────────────────────────────"; }
hdr()  { echo; line; echo "## $*"; line; }

hdr "A. CORE4 (new, isolated 188xx)"
for spec in hermes:18890 jarvis:18891 openclaw:18892 harvey:18893; do
    name="${spec%%:*}"; port="${spec##*:}"
    body="$(curl -fsS --max-time 3 "http://127.0.0.1:$port/health" 2>/dev/null || true)"
    if [[ -n "$body" ]]; then
        echo "✓ $name :$port  →  $body"
    else
        echo "✗ $name :$port  (down)"
    fi
done

hdr "B. LEGACY AGENT / ORCHESTRATION SERVICES (systemd)"
LEGACY_SVCS=(
    galaxia-core galaxia-jarvis galaxia-dispatcher galaxia-workforce-supervisor
    galaxia-dashboard
    hermes-gateway-jarvis hermes-gateway-legal hermes-gateway-researcher
    hermes-dashboard
    empire empire-semantic
)
for svc in "${LEGACY_SVCS[@]}"; do
    if systemctl list-unit-files "${svc}.service" >/dev/null 2>&1 \
       && systemctl cat "${svc}.service" >/dev/null 2>&1; then
        state="$(systemctl is-active "${svc}.service" 2>/dev/null)"
        desc="$(systemctl show -p Description --value "${svc}.service" 2>/dev/null)"
        exec="$(systemctl show -p ExecStart --value "${svc}.service" 2>/dev/null | sed -E 's/.*path=([^ ;]+).*argv\[\]=([^;]*).*/\1 | \2/')"
        wd="$(systemctl show -p WorkingDirectory --value "${svc}.service" 2>/dev/null)"
        echo "● ${svc}  [${state}]"
        echo "    desc: ${desc}"
        echo "    exec: ${exec}"
        [[ -n "$wd" ]] && echo "    cwd:  ${wd}"
    fi
done

hdr "C. LEGACY OPENCLAW (:18789) + RELATED LISTENERS"
ss -tlnp 2>/dev/null | grep -E ':(18789|18790|18791|18792)\b' || echo "(none on 18789-18792)"
opid="$(ss -tlnp 2>/dev/null | grep -oE ':18789\b.*pid=[0-9]+' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
if [[ -n "${opid:-}" ]]; then
    echo "openclaw :18789 cmdline:"
    tr '\0' ' ' < "/proc/$opid/cmdline" 2>/dev/null; echo
fi

hdr "D. HERMES CLI"
if command -v hermes >/dev/null 2>&1; then
    echo "path: $(command -v hermes)"
    hermes --version 2>/dev/null || echo "(version unknown)"
fi

hdr "E. ALL AGENT-ISH LISTENERS (python/node/uvicorn)"
ss -tlnp 2>/dev/null \
  | grep -E 'python|node|uvicorn|streamlit' \
  | sed -E 's/.*(127\.0\.0\.1|0\.0\.0\.0|\[::\]):([0-9]+).*users:\(\("([^"]+)".*pid=([0-9]+).*/  :\2  \3 (pid \4)/' \
  | sort -t: -k2 -n -u

hdr "F. OLLAMA MODELS (shared backend)"
ollama list 2>/dev/null | head -20 || echo "(ollama not reachable)"

echo; line
echo "Audit done. Core4 = 188xx. Legacy agent layer summarized above."
echo "Paste this whole output back for the overlap matrix + recommendation."
line
