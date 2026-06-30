# X MCP OAuth Setup

> Ziel: Echten X MCP-Zugang für Hermes-Archi aktivieren.

## Option A: X Developer API Key (empfohlen für Hermes-Archi)

1. Gehe zu https://developer.x.com/
2. Erstelle ein kostenloses Developer-Konto (wenn noch nicht vorhanden)
3. Lege ein neues **Project** an
4. Erstelle eine **App** im Project
5. Unter „Keys and Tokens“ generiere:
   - API Key
   - API Secret
   - Bearer Token (für read-only reicht oft dieser)
6. Setze in deiner Shell:
   ```bash
   export X_API_KEY=dein-bearer-token-oder-api-key
   ```
7. Führe aus:
   ```bash
   bash ~/ai-empire/projects/hermes-archi/control-plane/hermes/x_mcp_setup.sh
   ```

### Wichtig
- Für `search_recent` brauchst du den **Basic** oder **Pro** Tier.
- Basic ist kostenlos, aber mit Rate Limits.
- Pro kostet ~$100/Monat und hat mehr Requests.
- Für den Start reicht Basic.

## Option B: Hosted X MCP (neu, weniger klar)

X hat einen "hosted MCP" angekündigt, der angeblich "no setup" erfordert. Details:
- https://docs.x.com/tools/mcp
- Möglicherweise OAuth-basiert über X-Login
- Noch nicht vollständig dokumentiert (Stand 2026-06-30)

Falls verfügbar, kann OpenClaw/Cursor/Grok direkt darauf zugreifen. Für Hermes-Archi empfehlen wir aber Option A, weil deterministisch und lokal steuerbar.

## Was danach passiert

Wenn `x_mcp_setup.sh` erfolgreich ist:
1. `agents/research/x_trends.py` schaltet auf echten X-MCP-Modus um
2. Mock-Fallback wird nur noch genutzt, wenn X MCP fehlschlägt
3. X Trends 24h im Dashboard zeigen echte Daten
4. Writer-Agent kann echte Trends zu Content verarbeiten

## Kosten

| Tier | Kosten | Reicht für |
|------|--------|------------|
| Free | $0 | sehr wenige Tests |
| Basic | $0 / gering | tägliche Trends |
| Pro | ~$100/Monat | hohes Volumen |

Empfehlung: Basic starten, wenn Limits greifen, upgraden.
