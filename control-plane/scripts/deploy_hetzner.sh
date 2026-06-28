#!/usr/bin/env bash
# Core4 Hetzner Deployment Script
# Usage: bash control-plane/scripts/deploy_hetzner.sh
#
# Idempotent — safe to re-run after pulling fresh code.
# Run from repo root.

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; NC='\033[0m'

step()  { echo -e "\n${BLUE}=== $* ===${NC}"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
fail()  { echo -e "${RED}✗ $*${NC}"; exit 1; }

# ── Locate repo root ─────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
ok "Repo root: $REPO_ROOT"

# ── 1. Prerequisites ─────────────────────────────────────────────────────────
step "1/9  Prerequisites"

command -v python3 >/dev/null   || fail "python3 not installed"
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
[[ "$(printf '%s\n' "3.11" "$PY_VER" | sort -V | head -n1)" == "3.11" ]] \
    || fail "Python >= 3.11 required (have $PY_VER)"
ok "Python $PY_VER"

command -v pip3 >/dev/null || command -v pip >/dev/null || fail "pip not installed"
ok "pip available"

if command -v ollama >/dev/null; then
    ok "ollama installed"
    OLLAMA_AVAILABLE=1
else
    warn "ollama not found — LLM features will be degraded"
    OLLAMA_AVAILABLE=0
fi

if command -v node >/dev/null && command -v npm >/dev/null; then
    ok "node $(node --version) / npm available"
    NODE_AVAILABLE=1
else
    warn "node/npm not found — Telegram bot can't run"
    NODE_AVAILABLE=0
fi

# ── 2. Git update ────────────────────────────────────────────────────────────
step "2/9  Git status"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "$LOCAL")
if [[ "$LOCAL" != "$REMOTE" ]]; then
    warn "Branch is behind remote. Pulling..."
    git pull --ff-only
fi
ok "Branch: $(git branch --show-current) @ $(git rev-parse --short HEAD)"

# ── 3. Python dependencies ───────────────────────────────────────────────────
step "3/9  Python dependencies"
if [[ -d "$REPO_ROOT/.venv" ]]; then
    ok "Using existing .venv"
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.venv/bin/activate"
else
    python3 -m venv "$REPO_ROOT/.venv"
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.venv/bin/activate"
    ok "Created .venv"
fi

pip install --upgrade pip -q
pip install -r control-plane/requirements.txt -q
ok "Deps installed"

# ── 4. .env file ─────────────────────────────────────────────────────────────
step "4/9  Configuration"
ENV_FILE="$REPO_ROOT/control-plane/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    cp "$REPO_ROOT/control-plane/.env.example" "$ENV_FILE"
    warn "Created control-plane/.env from template — REVIEW IT before next deploy"
else
    ok "control-plane/.env exists"
fi

TG_ENV="$REPO_ROOT/integrations/telegram/.env"
if [[ ! -f "$TG_ENV" ]] && [[ -f "$REPO_ROOT/control-plane/telegram/.env.example" ]]; then
    cp "$REPO_ROOT/control-plane/telegram/.env.example" "$TG_ENV"
    warn "Created integrations/telegram/.env from template — fill in TELEGRAM_BOT_TOKEN + topic IDs"
fi

# Load config so EVERY subsequent step (start, health, tests) uses the
# configured ports — critical when running Core4 on the isolated 188xx range
# alongside legacy services that already own 18789-18792.
set -a; . "$ENV_FILE"; set +a
ok "Loaded config — Hermes:$HERMES_PORT Jarvis:$JARVIS_PORT OpenClaw:$OPENCLAW_PORT Harvey:$HARVEY_PORT"

# ── 5. Storage directories ───────────────────────────────────────────────────
step "5/9  Storage directories"
sudo_or_not() { if [[ $EUID -eq 0 ]]; then "$@"; else sudo "$@"; fi; }

for dir in /var/lib/hermes/goals /var/lib/jarvis /var/lib/openclaw /var/lib/harvey/legal_usage; do
    if [[ ! -d "$dir" ]]; then
        sudo_or_not mkdir -p "$dir"
        # chown the dir itself only — NEVER its parent (would recurse all of /var/lib)
        if [[ $EUID -ne 0 ]]; then
            sudo_or_not chown -R "$USER":"$USER" "$dir"
        fi
    fi
    ok "$dir"
done

mkdir -p "$REPO_ROOT/control-plane/run"
ok "run/ dir ready"

# ── 6. Ollama models ─────────────────────────────────────────────────────────
step "6/9  Ollama models"
if [[ "$OLLAMA_AVAILABLE" == "1" ]]; then
    if ! pgrep -x ollama >/dev/null; then
        warn "ollama daemon not running — starting in background"
        nohup ollama serve >> "$REPO_ROOT/control-plane/run/ollama.log" 2>&1 &
        sleep 3
    fi
    ok "ollama daemon running"

    REQUIRED_MODELS=(qwen3:30b-a3b deepseek-r1:32b nomic-embed-text)
    AVAILABLE=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

    for model in "${REQUIRED_MODELS[@]}"; do
        if echo "$AVAILABLE" | grep -q "^${model}$"; then
            ok "model $model present"
        else
            warn "pulling $model (this can take a while)..."
            ollama pull "$model" || warn "pull failed for $model — continuing"
        fi
    done
else
    warn "Skipping Ollama setup (not installed)"
fi

# ── 7. Stop existing daemons ─────────────────────────────────────────────────
step "7/9  Stop existing daemons"
if [[ -x "$REPO_ROOT/control-plane/scripts/stop_all.sh" ]]; then
    "$REPO_ROOT/control-plane/scripts/stop_all.sh" 2>&1 || true
    ok "stopped"
fi

# ── 8. Start all daemons ─────────────────────────────────────────────────────
step "8/9  Start daemons"
"$REPO_ROOT/control-plane/scripts/start_all.sh"

# ── 9. Tests ─────────────────────────────────────────────────────────────────
step "9/9  Tests"
# pytest is a dev-only dep (not in requirements.txt) — ensure it for the self-check
if ! python -m pytest --version >/dev/null 2>&1; then
    warn "pytest not in venv — installing for self-check"
    python -m pip install -q pytest || warn "pytest install failed — skipping tests"
fi

echo "--- Unit tests ---"
python -m pytest control-plane/tests/test_unit.py -v --tb=short 2>&1 | tail -20

echo ""
echo "--- E2E tests ---"
python -m pytest control-plane/tests/test_e2e.py -v --tb=short 2>&1 | tail -25

# ── Optional: Telegram bot ───────────────────────────────────────────────────
step "Telegram Bot (optional)"
if [[ "$NODE_AVAILABLE" == "1" ]]; then
    if [[ -f "$TG_ENV" ]] && grep -q "^TELEGRAM_BOT_TOKEN=." "$TG_ENV" 2>/dev/null; then
        echo "Telegram bot config detected."
        echo "Start with: bash $REPO_ROOT/control-plane/telegram/start_bot.sh"
    else
        warn "Telegram bot not configured. Edit $TG_ENV first:"
        echo "  - Set TELEGRAM_BOT_TOKEN"
        echo "  - Set TELEGRAM_TOPIC_JARVIS, _HERMES, _OPENCLAW, _HARVEY"
        echo "Then run: bash $REPO_ROOT/control-plane/telegram/start_bot.sh"
    fi
else
    warn "node/npm not available — skip Telegram bot"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
step "Done"
echo ""
echo "Core4 deployed. URLs:"
echo "  Hermes   http://127.0.0.1:${HERMES_PORT}/health"
echo "  Jarvis   http://127.0.0.1:${JARVIS_PORT}/health"
echo "  OpenClaw http://127.0.0.1:${OPENCLAW_PORT}/health"
echo "  Harvey   http://127.0.0.1:${HARVEY_PORT}/health"
echo ""
echo "Logs in:    $REPO_ROOT/control-plane/run/"
echo "Stop with:  bash $REPO_ROOT/control-plane/scripts/stop_all.sh"
echo ""
echo "Quick test:"
echo "  curl -s http://127.0.0.1:${JARVIS_PORT}/chat \\"
echo "    -H 'content-type: application/json' \\"
echo "    -d '{\"text\":\"Hi Jarvis\",\"user_id\":\"maurice\"}' | jq"
