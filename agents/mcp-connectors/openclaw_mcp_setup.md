# OpenClaw X MCP Setup

1. OpenClaw starten: openclaw mcp add x
2. Transport waehlen: stdio oder sse
3. Command eintragen: npx -y @x/mcp-server
4. Env: X_API_KEY=YOUR_KEY
5. Test: openclaw mcp test x

Falls @x/mcp-server nicht existiert:
- Offizielle Doku pruefen: https://docs.x.com/tools/mcp
- Eventuell ist der Server ueber SSE-URL https://x.com/i/mcp erreichbar
