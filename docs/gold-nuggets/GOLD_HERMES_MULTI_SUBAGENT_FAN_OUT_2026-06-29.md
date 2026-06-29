# 💰 Gold Nugget: Hermes Multi-Subagent Fan-Out Pattern

**Datum:** 2026-06-29  
**Quelle:** Maurice Insight + aiedge_ Hermes Template  
**Status:** Roherkenntnis → Produkt-/Skill-Kandidat

## Trigger Phrase

> "Launch multiple sub-agents for [task]."

## Full Template

```
Launch multiple sub-agents for [TASK].
Split the work into: [N angles/subtasks - or let Hermes decide]
Each agent should: work independently, then report back
Cross-verify: have agents check each other's findings before you finalize
Merge into: [ONE clean output - report / code / summary]
Work autonomously. Report back when all agents are done.
```

## Beispiele

- **Research:** "Launch multiple sub-agents to research [topic] from 4 different angles, then merge into one report."
- **Coding:** "Launch multiple sub-agents to build [feature] - one on backend, one on frontend, one on tests."
- **Debugging:** "Launch multiple sub-agents to investigate this bug from different hypotheses, then converge on the root cause."
- **Content:** "Launch multiple sub-agents to draft 3 versions of [content] in different tones, then pick the strongest."

## Power Tips

- Specify a number: "launch 5 sub-agents" for explicit control
- Save as a skill once it works well - reuse the same orchestration
- Always ask for cross-verification - prevents conflicting outputs
- Connect MCPs first - subagents with live data beat ones without

## Warum wertvoll

- **Effizienz:** Statt eines Agents durch viele Schritte → parallele Spezialisierung.
- **Qualität:** Cross-Verification reduziert Halluzinationen und Loops.
- **Skalierung:** Ein Prompt → mehrere Agenten → gemergtes Ergebnis.
- **Differenzierung:** Viele Single-Agent-Setups; Team-of-Agents ist Kingmaker-Feature.

## Monetarisierungswinkel

1. **Skill/Template für Hermes:** `hermes swarm run --prompt "..."` → fan-out + merge.
2. **Vertical Agent Factory:** Jede Lane (Content, Code, Research, Sales) als Mini-Team.
3. **Service/Agent-Team-as-a-Service:** Kunden-Prompt → 3-5 Spezial-Agenten → Deliverable.
4. **Karpathy Agent OS Starter Kit:** Multi-Agent-Discipline als Kernmodul.
5. **Consulting:** BMA/Technik-Unternehmen bekommen ihr eigenes Agent-Team.

## Nächste Schritte

1. Hermes-Subagent-Skill template bauen (`skills/orchestration/swarm-fan-out`).
2. Erstes Vertical lane prototypen (Content/Revenue oder Code Review).
3. Integration mit `100x-self-improvement-loop` für nach jeder Swarm-Run.
4. Cross-verification + merge Logik deterministisch machen (JSON Schema, Hooks).

## Verwandte Projekte

- Hermes Agent System (`~/.hermes/`)
- Self-Improvement 100x Loop (`~/.hermes/skills/orchestration/self-improvement-100x-loop`)
- Vertical Agent Factory (NEXT.md)
- Karpathy Agent OS / Masterclass (`09_LIBRARY/github/andrej-karpathy-skills`)
