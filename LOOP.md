# Loop Configuration — AI Empire / Hermes-Archi

## Active Loops

| Pattern | Cadence | Status | Command |
|---------|---------|--------|---------|
| Daily Triage | 1d | L1 report-only | Read memory, surface next actions |
| Launch Monitor | 1h | L1 | Watch PayPal / traffic / engagement |
| Dependency Sweeper | 1w | L1 | Check npm/pip CVEs, report only |

## Human Gates

- No auto-merge on main
- No payment processing automation until first 10 manual sales
- No auto-post on social accounts
- All product releases require human approval

## Budget

- Max tokens/day: 200k
- Kill switch: `loop-pause-all` flag in STATE.md
- Estimate: `npx @cobusgreyling/loop-cost --pattern daily-triage`

## Links

- Pattern library: library/loop-engineering-cobusgreyling/patterns/
- Launch playbook: products/one-person-ai-agent-company/go-to-market/LAUNCH_PLAYBOOK.md\n

## Adaptive Loop Engine

Runs continuously: analyzes dopamine score, neural bus patterns, and lessons. Proposes new Silverloops. Currently L1 report-only; emperor approves implementations.

Command: `python3 agents/agent-os-harness/adaptive_loop_engine.py`

---

## First-Principles Loop Logic

Nicht:
```
KI macht Schritt
↓
Maurice genehmigt
↓
KI macht nächsten Schritt
```
Das ist ein langsamer Loop. Das ist Human-as-Brake-Pedal.

Sondern:
```
Maurice definiert Ziel
↓
Hermes versteht Constraints
↓
Hermes baut Plan
↓
Maurice prüft Entscheidungspunkte
↓
Hermes führt operative Arbeit aus
↓
Hermes prüft Ergebnis
↓
Maurice entscheidet echte Verantwortungskanten
↓
Hermes schreibt neue Regeln zurück
↓
Nächster Loop ist besser
```

**Kernfrage pro Aktion:** Ist das nur Arbeit oder Verantwortung?

- Arbeit → Hermes macht.
- Verantwortung → Maurice entscheidet.
- Unklar → Decision Card.

Siehe `PHILOSOPHY.md` für vollständige First-Principles-Ausführung.
