#!/bin/bash
# X MCP Setup — holt Zugang und testet echten X MCP
set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
cd "$REPO"

echo "=== X MCP Setup ==="
echo ""

# Check if X_API_KEY is set
if [ -z "${X_API_KEY:-}" ]; then
    echo "❌ X_API_KEY ist nicht gesetzt."
    echo ""
    echo "Schritt-für-Schritt zur Beschaffung:"
    echo "1. Öffne https://developer.x.com/"
    echo "2. Melde dich mit deinem X-Account an"
    echo "3. Erstelle ein neues Project + App"
    echo "4. Generiere einen API Key (Empfehlung: 'Read'-Scope reicht für search/timeline)"
    echo "5. Kopiere den Key und führe aus: export X_API_KEY=dein-key"
    echo ""
    echo "Alternativ: Wenn der X-hosted-MCP via OAuth funktioniert, folge der Anleitung in:"
    echo "   control-plane/hermes/X_MCP_OAUTH_SETUP.md"
    echo ""
    echo "Danach erneut: bash control-plane/hermes/x_mcp_setup.sh"
    exit 1
fi

echo "✅ X_API_KEY ist gesetzt"

# Test if @x/mcp-server is installable
echo "Teste @x/mcp-server..."
if ! npx -y @x/mcp-server --help >/dev/null 2>&1; then
    echo "⚠️ @x/mcp-server konnte nicht ausgeführt werden. Prüfe npm/Internet."
    exit 2
fi

echo "✅ @x/mcp-server verfügbar"

# Test the actual X MCP search_recent
echo "Teste X MCP search_recent..."
RESULT=$(npx -y @x/mcp-server search_recent '{"query": "AI agent", "max_results": 3}' 2>&1 || true)

if echo "$RESULT" | grep -q "error\|rate limit\|unauthorized\|forbidden"; then
    echo "⚠️ X MCP erreichbar, aber Antwort enthält Fehler:"
    echo "$RESULT" | head -20
    exit 3
fi

if echo "$RESULT" | grep -q "data\|tweet\|result"; then
    echo "✅ X MCP liefert echte Daten!"
    echo "$RESULT" | head -40
    exit 0
else
    echo "⚠️ Unklare Antwort:"
    echo "$RESULT" | head -20
    exit 4
fi
