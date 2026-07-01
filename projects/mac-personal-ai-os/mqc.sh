#!/bin/bash
# MQC — Mac Quality Control / Personal AI OS Entry Point
# Usage: ./mqc.sh [index | query | bridge | assist | learn]

DIR="$(cd "$(dirname "$0")" && pwd)"
CORE="$DIR/core"
VENV="/Users/maurice/ai-empire/projects/hermes-archi/.venv"

if [ -f "$VENV/bin/activate" ]; then
  source "$VENV/bin/activate"
fi

case "${1:-status}" in
  index)
    echo "[mqc] Indexing Mac data..."
    python3 "$CORE/mac_data_indexer.py"
    ;;
  query)
    shift
    python3 "$CORE/mac_query.py" "$@"
    ;;
  bridge|assist)
    shift
    python3 "$CORE/hermes_openclaw_bridge.py" "$@"
    ;;
  learn)
    echo "[mqc] Open demonstration capture template:"
    open "$CORE/demonstration_capture_template.md"
    ;;
  status|*)
    echo "MQC — Mac Personal AI OS"
    echo ""
    echo "Usage:"
    echo "  ./mqc.sh index              # Rebuild Mac data index"
    echo "  ./mqc.sh query --find NAME  # Query indexed data"
    echo "  ./mqc.sh bridge 'TEXT'      # Route command to Hermes"
    echo "  ./mqc.sh learn              # Open demonstration capture template"
    echo ""
    echo "Index:  ~/.mqc/index.jsonl"
    echo "DB:     ~/.mqc/mac_data.db"
    echo "Bridge: core/hermes_openclaw_bridge.py"
    ;;
esac
