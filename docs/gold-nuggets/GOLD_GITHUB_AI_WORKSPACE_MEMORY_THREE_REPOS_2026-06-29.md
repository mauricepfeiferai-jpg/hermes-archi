# 💰 Gold Nugget: GitHub as AI Workspace Memory — Three Repos for PM/Agent Work

**Datum:** 2026-06-29  
**Quelle:** Aakash Gupta + Shubham Saboo — "Control for Everything You Build With AI"  
**Status:** Roherkenntnis → Hermes/AI-Empire-Workspace-Policy

## Die Erkenntnis

> GitHub ist nicht mehr nur ein Engineering-Tool. Es ist das Gedächtnis für alles, was man mit AI baut.
>
> Drei Repos decken 90% der Arbeit ab:
> 1. **Private Workspace** — CLAUDE.md, persönliche Skills, Autoresearch-Configs.
> 2. **Shared Tools** — Skills/Templates ohne persönlichen Kontext, forkbar in 30 Sekunden.
> 3. **Per-Project Repo** — PLANNING.md, Eval-Kriterien, Code, komplette Build-History.

## Der Daily Loop

> pull → branch → edit → commit → push → PR → merge

Alles per natürlicher Sprache an Claude Code. Kein Git-Syntax notwendig.

## Vier Version-Control-Workflows

| Workflow | Problem | Lösung durch Git |
|---|---|---|
| **Skill rollback** | Skill editiert, Output wird schlecht | Ein Command → vorherige Version wiederherstellen, Diff zeigt die Ursache |
| **CLAUDE.md pruning** | Datei >200 Zeilen → Claude ignoriert Regeln | Monatlicher Diff zeigt Drift, Überflüssiges wird gekürzt |
| **Autoresearch logging** | 100 Iterationen über Nacht | Git-Log IST das Experiment-Log: Wins behalten, Losses revertieren |
| **Eval versioning** | Score sinkt 0.82 → 0.71 | Commit-History sagt: Modell-Regression vs. Scoring-Änderung |

## Warum wertvoll für Maurice

- **Backup:** Maschine stirbt → 2 Minuten Setup auf neuer Machine.
- **Cross-Device:** Gleiches Setup auf Mac, iPhone (Claude iOS), Hetzner.
- **Reproduzierbarkeit:** Jede AI-Ausgabe hat eine Version.
- **Team-Skalierung:** Shared-Tools-Repo für Kunden/Partner/Mitarbeiter.
- **Autoresearch:** Hermes/OpenClaw-Agent-Loops versionieren Erfolge/Verluste.

## Sicherheitsregeln

- Private Repo ≠ Privacy-Strategie.
- Vor Push: API-Keys, .env, Kundendaten, interne Strategie, HR-Daten, Slack-Exports, sensitive Screenshots entfernen.
- `.gitignore` zuerst, dann Secret-Scan, dann push.

## Übertragung auf AI Empire

- **Repo 1 (Private Workspace):** `~/.claude/`, `~/.codex/skills/`, `~/.hermes/`, `~/.openclaw/workspace/ai-empire/`
- **Repo 2 (Shared Tools):** `karpathy-guidelines`, `skill-picker`, `swarm-fan-out`, `self-improvement-100x-loop` — persönlichen Kontext entfernt
- **Repo 3 (Per-Project):** `hermes-archi`, `andrej-karpathy-skills`, zukünftige Produkte

## Monetarisierungswinkel

1. **AI Workspace Migration Service:** Andere Techniker/PMs auf GitHub-basierte AI-Workspaces umstellen.
2. **Starter Repo:** "AI Empire Workspace Template" mit .gitignore, CLAUDE.md, Skill-Ordnern, Eval-Templates.
3. **Team OS / Shared Skills:** Wiederkehrende Skills als forkbares Repo für BMA-Dienstleister.
4. **Autoresearch-as-a-Product:** Nightly loops mit Git-Versionierung für Kunden-Anwendungsfälle.
5. **Karpathy Agent OS Erweiterung:** "Version Control Module" als Core-Discipline.

## Nächste Schritte

1. Bestehende `hermes-archi`-Struktur auf 3-Repo-Modell prüfen.
2. Private-Workspace-Policy definieren: was kommt in GitHub, was bleibt lokal/verschlüsselt.
3. `.gitignore` + Secret-Scan in allen AI-Empire-Repos vereinheitlichen.
4. Claude-Code-Git-Workflow als Skill dokumentieren: `skills/orchestration/git-workflow-ai/`.
5. Shared-Tools-Repo-Plan für BMA-fokussierte Skills erstellen.

## Verwandte Projekte

- Hermes-Archi (`~/ai-empire/projects/hermes-archi`)
- Karpathy Agent OS / Masterclass (`09_LIBRARY/github/andrej-karpathy-skills`)
- Swarm Fan-Out Skill (`~/.hermes/skills/orchestration/swarm-fan-out`)
- Self-Improvement 100x Loop (`~/.hermes/skills/orchestration/self-improvement-100x-loop`)
- Skill Picker (`~/.codex/skills/skill-picker`)
