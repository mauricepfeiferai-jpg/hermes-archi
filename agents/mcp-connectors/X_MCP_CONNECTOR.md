# X MCP Connector — AI Empire Agent OS

## Status

- Offizieller X MCP Server: https://docs.x.com/tools/mcp
- Verbindet Grok, Cursor, Claude, Codex, OpenClaw mit X API
- Echtzeit-Zugriff auf Posts, Trends, Reaktionen

## MCP Server URL (vermutet)

- Web: https://x.com/i/mcp
- Docs: https://docs.x.com/tools/mcp
- Transport: SSE oder stdio (offizielle Docs pruefen)

## Claude Desktop / Codex Config

```json
{
  "mcpServers": {
    "x": {
      "command": "npx",
      "args": ["-y", "@x/mcp-server"],
      "env": {
        "X_API_KEY": "YOUR_X_API_KEY"
      }
    }
  }
}
```

## OpenClaw Config

In OpenClaw mcp integrations eintragen:
- server name: x
- transport: stdio oder sse
- env: X_API_KEY

## Hermes-Archi Integration

- agents/research/x_trends.py wrappt X MCP / Fallback
- ops/cron/26-x-trends.sh laeuft taeglich 08:30
- Output: state/x/trends_YYYY-MM-DD.json
- Neural Bus Event: x.trends.discovered
- Empfaenger: emperor, writer, researcher, openclaw_main

## Wichtig

Ohne X API Key laeuft das Skript im Fallback-Modus (Kimi/OpenAI Trend-Analyse).
Sobald API Key vorhanden ist, schaltet es auf echten X MCP um.
