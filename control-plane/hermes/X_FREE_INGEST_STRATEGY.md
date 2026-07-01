# X Free Ingest Strategy

> Kein X API Key. Keine 200 EUR/Monat. Kostenloser X-Zugriff für Hermes/Hecate.

## Status

- X Premium API: abgelehnt (zu teuer)
- Jina Reader für x.com: blockiert (451 SecurityCompromiseError)
- Agent Reach + Twitter Cookie: möglich, benötigt Maurice's eigenen Account-Cookie
- Trend-Proxies: Reddit + HN + RSS funktionieren ohne Auth

## Akzeptierte kostenlose Pfade

### 1. Agent Reach + Twitter Cookie (empfohlen)

Tool: `twitter-cli` via Agent Reach
Setup: Browser-Cookie exportieren, lokal speichern
Kosten: $0
Limit: Eigener Account, Rate-Limits von X

**Voraussetzungen:**
- X Account vorhanden
- Desktop-Browser (Chrome/Safari/Edge)
- Cookie-Export Extension oder DevTools

**Schritte:**
1. Im Browser auf x.com einloggen
2. Cookie `auth_token` und/oder `ct0` kopieren
3. In `~/.agent-reach/cookies/twitter.json` speichern
4. `agent-reach doctor` ausführen → Twitter/X sollte grün werden
5. Test: `twitter search "AI agents" --limit 5`

**Maurice-Go nötig für:** Cookie-Export.

---

### 2. Jina Reader (nicht für X, aber für Web)

- Für x.com blockiert
- Für andere Webseiten weiterhin nutzbar
- Bleibt im Web-Ingest-Stack

---

### 3. Trend-Proxies (kein X nötig)

Reddit, Hacker News, arXiv, RSS-Feeds liefern AI-Trends ohne X:

| Quelle | Was liefert | Status |
|--------|-------------|--------|
| Hacker News | Tech/AI Diskussionen | ✅ kostenlos |
| Reddit r/LocalLLaMA | Open-Source AI Trends | ✅ kostenlos |
| arXiv cs.AI RSS | Paper-Trends | ✅ kostenlos |
| GitHub Search API | Repo/Projekt-Trends | ✅ kostenlos |
| RSS-Feeds (Blogs) | Langform-Trends | ✅ kostenlos |

Diese Quellen können X Trends ersetzen, solange es um AI-Agenten/Engineering geht.

---

### 4. Manueller Copy-Paste für wichtige X-Posts

Für X-to-Wisdom Engine:
- Maurice kopiert Post-URL + Text
- Hermes verarbeitet nach First Principles
- Kein API, kein Scraper nötig

Dies ist der robusteste Pfad für hochwertige Einzelposts.

---

## Empfohlene Strategie

1. **Sofort:** Trend-Proxies als primäre Trend-Quelle nutzen (RSS, HN, Reddit, arXiv, GitHub)
2. **Parallel:** Agent Reach Twitter Cookie Setup vorbereiten (Maurice-Go für Cookie-Export)
3. **Für X-to-Wisdom:** Manueller Copy-Paste als Standardpfad
4. **X API / Premium-Abos:** nicht in Betracht ziehen

## Impact auf `x_trends.py`

- Mock-Demo-Modus bleibt als Fallback
- Echter X MCP wird nicht verwendet (kein API Key)
- Agent Reach `twitter search` wird integriert, sobald Cookie vorhanden
- Trend-Proxy-Quellen werden primär

## Nächste Aktion

1. Cookie-Export-Anleitung bereitstellen
2. `x_trends.py` auf Trend-Proxies umstellen
3. X-to-Wisdom Engine auf manuellen Ingest optimieren
