#!/usr/bin/env bash
# Core4 Memory Sync — pull Maurice's data goldmines into Jarvis Memory,
# then export the unified view to Obsidian.
#
# Designed to run nightly (cron) or manually. Idempotent.
#
# Configure source paths via env (all optional — missing ones are skipped):
#   SCHATZKAMMER_DB   path to schatzkammer.db
#   LEGAL_DRAFTS_DIR  dir of legal .md analyses (e.g. ~/gpe-night/drafts)
#   TRANSFER_DIR      dir of analysis .md (e.g. ~/transfer)
#   LEGAL_TEXT_DIR    OCR-extracted texts (e.g. ~/legal-master/03_text)
#   OBSIDIAN_VAULT    target Obsidian vault root
#   EMBED=1           also compute embeddings (slow; default off)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUNTIME="$REPO_ROOT/control-plane/jarvis/runtime"

# Use venv python if present
PY="python3"
[[ -x "$REPO_ROOT/.venv/bin/python" ]] && PY="$REPO_ROOT/.venv/bin/python"

EMBED_FLAG=""
[[ "${EMBED:-0}" == "1" ]] && EMBED_FLAG="--embed"

echo "=== Core4 Memory Sync — $(date '+%Y-%m-%d %H:%M') ==="

# ── 1. Import sources ────────────────────────────────────────────────────────
if [[ -n "${SCHATZKAMMER_DB:-}" && -f "${SCHATZKAMMER_DB}" ]]; then
  echo "[import] schatzkammer: $SCHATZKAMMER_DB"
  "$PY" "$RUNTIME/importer.py" --source-db "$SCHATZKAMMER_DB" \
       --label schatzkammer --source schatzkammer $EMBED_FLAG
fi

if [[ -n "${LEGAL_DRAFTS_DIR:-}" && -d "${LEGAL_DRAFTS_DIR}" ]]; then
  echo "[import] legal drafts: $LEGAL_DRAFTS_DIR"
  "$PY" "$RUNTIME/importer.py" --source-dir "$LEGAL_DRAFTS_DIR" \
       --label legal --source drafts $EMBED_FLAG
fi

if [[ -n "${TRANSFER_DIR:-}" && -d "${TRANSFER_DIR}" ]]; then
  echo "[import] transfer analyses: $TRANSFER_DIR"
  "$PY" "$RUNTIME/importer.py" --source-dir "$TRANSFER_DIR" \
       --label analysis --source transfer $EMBED_FLAG
fi

if [[ -n "${LEGAL_TEXT_DIR:-}" && -d "${LEGAL_TEXT_DIR}" ]]; then
  echo "[import] legal OCR text: $LEGAL_TEXT_DIR"
  "$PY" "$RUNTIME/importer.py" --source-dir "$LEGAL_TEXT_DIR" \
       --label legal_ocr --source legal-master $EMBED_FLAG
fi

# ── 2. Stats ─────────────────────────────────────────────────────────────────
echo "[stats]"
"$PY" "$RUNTIME/importer.py" --stats

# ── 3. Export to Obsidian ────────────────────────────────────────────────────
if [[ -n "${OBSIDIAN_VAULT:-}" ]]; then
  echo "[export] Obsidian: $OBSIDIAN_VAULT"
  "$PY" "$RUNTIME/obsidian_export.py" --vault "$OBSIDIAN_VAULT"
else
  echo "[export] skipped (set OBSIDIAN_VAULT to enable)"
fi

echo "=== Memory Sync done ==="
