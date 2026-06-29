# 💰 Gold Nugget: One-Person AI Agent Company — 7 Agents, 10 Cron Jobs, 0 Employees

**Datum:** 2026-06-29  
**Quelle:** Maurice Insight — AI-native Solo-Unternehmen  
**Status:** Roherkenntnis → Template-/Produkt-Kandidat

## Die Erkenntnis

> So führt man 2026 eine One-Person AI-Agent-Company: 7 AI Agents, 10 Cron Jobs, 0 human employees.
>
> Jede Rolle ist ein Ordner. Jedes Job-Description ist eine `.md`-Datei. Keine Standups, kein Slack, keine Payroll.
>
> Jeder Agent macht Review, Retro und Self-Improvement in der Loop.

## Kernprinzipien

- **Filesystem als Org-Chart:** Rollen = Ordner; Job-Descriptions = Markdown.
- **Cron als Manager:** 10 wiederkehrende Jobs steuern Ausführung.
- **Loop als Kultur:** Review → Retro → Self-Improvement nach jeder Run.
- **0 Human Employees:** Eine Person orchestriert, Agents führen aus.

## Struktur-Vorschlag

```
~/.agents/company/
├── ceo/               # Strategie, Ziele, Entscheidungen
├── cto/               # Architektur, Tech-Stack, Security
├── engineer/          # Code, Tests, Deployments
├── researcher/        # Markt, Trends, Wettbewerb
├── writer/            # Content, Copy, Dokumentation
├── sales/             # Leads, Angebote, Kundenkommunikation
├── ops/               # Cron, Monitoring, Buchhaltung, Compliance
└── loop/              # Review, Retro, Self-Improvement, Rule-Updates
```

## Cron-Jobs (Beispiel)

| # | Job | Frequenz | Agent |
|---|---|---|---|
| 1 | Tagesziele prüfen | 06:00 | CEO |
| 2 | Tech-Health-Check | 06:15 | CTO |
| 3 | Code-Review-Queue | 07:00 | Engineer |
| 4 | Trend-Scan | 08:00 | Researcher |
| 5 | Content-Ideen-Draft | 09:00 | Writer |
| 6 | Lead-Inbox-Triage | 10:00 | Sales |
| 7 | Angebotserstellung | 11:00 | Sales |
| 8 | Backup + Compliance | 18:00 | Ops |
| 9 | Daily Retro | 20:00 | Loop |
| 10 | Rule-Update + Improvement | 20:30 | Loop |

## LOOP (Review / Retro / Self-Improve)

1. **Review:** Output gegen Ziele/Qualitäts-Gates prüfen.
2. **Retro:** Was lief gut? Was blockiert? Was wiederholt sich?
3. **Self-Improve:** Regel/Gate/Template/Test/Dashboard patchen.
4. **Rule-Update-Log:** Dauerhafte Änderung dokumentieren.

## Monetarisierungswinkel

1. **Template/Starter-Kit:** "One-Person AI Agent Company in a Box" — 7 Ordner, 10 Cron-Jobs, Loop-Integration.
2. **Hermes Skill:** `hermes company init` erstellt Struktur, crontab und erste Jobs.
3. **BMA-Dienstleister-Variante:** Rollen spezialisiert auf Angebotserstellung, Norm-Check, Kundenkommunikation, Dokumentation.
4. **Consulting:** Setup für Solo-Gründer / kleine Dienstleister.
5. **Karpathy Agent OS Ergänzung:** Als Core-Modul "Company OS" im Starter Kit.

## Verwandte Projekte

- Hermes Agent System (`~/.hermes/`)
- Swarm Fan-Out Skill (`~/.hermes/skills/orchestration/swarm-fan-out`)
- Self-Improvement 100x Loop (`~/.hermes/skills/orchestration/self-improvement-100x-loop`)
- Karpathy Agent OS / Masterclass (`09_LIBRARY/github/andrej-karpathy-skills`)
- Vertical Agent Factory (NEXT.md)

## Nächste Schritte

1. Minimale Ordner-Struktur + Job-Description-Templates als Dateien anlegen.
2. 10 Beispiel-Cron-Jobs in Hermes-Cron-Format übersetzen.
3. Mit `100x-self-improvement-loop` verknüpfen: jede Agent-Run endet mit Review/Retro.
4. Erste BMA-spezifische Rollen definieren (z.B. `bma-estimator`, `bma-norm-checker`).
