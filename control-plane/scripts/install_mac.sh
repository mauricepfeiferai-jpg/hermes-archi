#!/usr/bin/env bash
# Core4 Mac Installer — one command, fully wired, permanent.
#
# What it does:
#   1. Auto-detects your data goldmines (schatzkammer, drafts, transfer, ...)
#   2. Auto-detects your iCloud Obsidian vault
#   3. Installs Python deps + ensures Core4 daemons are running
#   4. Runs the FIRST full memory sync (import → Jarvis brain → Obsidian)
#   5. Installs a launchd job so it re-syncs automatically every night at 03:00
#
# Run once:
#   bash control-plane/scripts/install_mac.sh
#
# Re-run anytime — it's idempotent.

set -uo pipefail

GREEN='\033[0;32m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
step() { echo -e "\n${BLUE}=== $* ===${NC}"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

# ── 1. Auto-detect data sources ──────────────────────────────────────────────
step "1/5  Detecting data sources"

find_first() { for p in "$@"; do [[ -e "${p/#\~/$HOME}" ]] && { echo "${p/#\~/$HOME}"; return; }; done; }

SCHATZKAMMER_DB="$(find_first ~/schatzkammer/schatzkammer.db ~/Schatzkammer/schatzkammer.db)"
LEGAL_DRAFTS_DIR="$(find_first ~/gpe-night/drafts ~/gpe-night/Drafts)"
TRANSFER_DIR="$(find_first ~/transfer ~/Transfer)"
LEGAL_TEXT_DIR="$(find_first ~/legal-master/03_text ~/legal-master/03_Text)"
RECHTSSTREIT_DIR="$(find_first ~/Rechtsstreit)"

[[ -n "${SCHATZKAMMER_DB:-}"  ]] && ok "schatzkammer:   $SCHATZKAMMER_DB"   || warn "schatzkammer.db not found"
[[ -n "${LEGAL_DRAFTS_DIR:-}" ]] && ok "gpe-night drafts: $LEGAL_DRAFTS_DIR" || warn "gpe-night/drafts not found"
[[ -n "${TRANSFER_DIR:-}"     ]] && ok "transfer:       $TRANSFER_DIR"       || warn "transfer not found"
[[ -n "${LEGAL_TEXT_DIR:-}"   ]] && ok "legal OCR text: $LEGAL_TEXT_DIR"     || warn "legal-master/03_text not found"
[[ -n "${RECHTSSTREIT_DIR:-}" ]] && ok "rechtsstreit:   $RECHTSSTREIT_DIR"   || warn "Rechtsstreit not found"

# ── 2. Auto-detect Obsidian vault ────────────────────────────────────────────
step "2/5  Detecting Obsidian vault"
ICLOUD_OBS="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents"
OBSIDIAN_VAULT=""
if [[ -d "$ICLOUD_OBS" ]]; then
  # Prefer a vault containing "Empire" or "AI", else first vault found
  OBSIDIAN_VAULT="$(find "$ICLOUD_OBS" -maxdepth 1 -type d \( -iname "*empire*" -o -iname "*ai*" \) 2>/dev/null | head -1)"
  [[ -z "$OBSIDIAN_VAULT" ]] && OBSIDIAN_VAULT="$(find "$ICLOUD_OBS" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)"
fi
[[ -z "$OBSIDIAN_VAULT" ]] && OBSIDIAN_VAULT="$(find_first ~/ObsidianVault ~/Obsidian)"
if [[ -n "$OBSIDIAN_VAULT" ]]; then
  ok "Obsidian vault: $OBSIDIAN_VAULT"
else
  OBSIDIAN_VAULT="$HOME/ObsidianVault"
  warn "No vault found — will create $OBSIDIAN_VAULT"
  mkdir -p "$OBSIDIAN_VAULT"
fi

# ── 3. Python deps + daemons ─────────────────────────────────────────────────
step "3/5  Dependencies + daemons"
PY="python3"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PY="$REPO_ROOT/.venv/bin/python"
  ok "using .venv"
else
  warn "no .venv — using system python3 (run deploy_hetzner.sh for a venv)"
fi
"$PY" -m pip install -q -r control-plane/requirements.txt 2>/dev/null && ok "deps ok" || warn "pip install skipped"

if ! curl -s http://127.0.0.1:18790/health >/dev/null 2>&1; then
  warn "Hermes not running — starting daemons"
  bash control-plane/scripts/start_all.sh >/dev/null 2>&1 || warn "could not start daemons"
  sleep 3
fi
curl -s http://127.0.0.1:18790/health >/dev/null 2>&1 && ok "daemons up" || warn "daemons not reachable (export still works, dashboard health will show ⚠️)"

# ── 4. First sync ────────────────────────────────────────────────────────────
step "4/5  First memory sync"
export SCHATZKAMMER_DB LEGAL_DRAFTS_DIR TRANSFER_DIR LEGAL_TEXT_DIR OBSIDIAN_VAULT
# Rechtsstreit as an extra source dir if present
if [[ -n "${RECHTSSTREIT_DIR:-}" ]]; then
  "$PY" control-plane/jarvis/runtime/importer.py --source-dir "$RECHTSSTREIT_DIR" \
       --label rechtsstreit --source rechtsstreit 2>/dev/null || true
fi
bash control-plane/scripts/memory_sync.sh

# ── 5. Nightly automation (launchd) ──────────────────────────────────────────
step "5/5  Nightly automation"
PLIST="$HOME/Library/LaunchAgents/com.pfeifer.core4.memorysync.plist"
mkdir -p "$HOME/Library/LaunchAgents"
LOG="$REPO_ROOT/control-plane/run/memory_sync.log"
mkdir -p "$REPO_ROOT/control-plane/run"

cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.pfeifer.core4.memorysync</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$REPO_ROOT/control-plane/scripts/memory_sync.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>SCHATZKAMMER_DB</key><string>${SCHATZKAMMER_DB:-}</string>
    <key>LEGAL_DRAFTS_DIR</key><string>${LEGAL_DRAFTS_DIR:-}</string>
    <key>TRANSFER_DIR</key><string>${TRANSFER_DIR:-}</string>
    <key>LEGAL_TEXT_DIR</key><string>${LEGAL_TEXT_DIR:-}</string>
    <key>OBSIDIAN_VAULT</key><string>$OBSIDIAN_VAULT</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PLISTEOF

launchctl unload "$PLIST" 2>/dev/null || true
if launchctl load "$PLIST" 2>/dev/null; then
  ok "nightly sync installed (daily 03:00) → $PLIST"
else
  warn "launchctl load failed — plist written, load manually: launchctl load $PLIST"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN} Core4 fully wired.${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo "Knowledge base:  $PY control-plane/jarvis/runtime/importer.py --stats"
echo "Obsidian:        open '$OBSIDIAN_VAULT/EMPIRE_CORE4/00_DASHBOARD.md'"
echo "Re-sync now:     bash control-plane/scripts/memory_sync.sh"
echo "Nightly:         automatic at 03:00 (launchd)"
