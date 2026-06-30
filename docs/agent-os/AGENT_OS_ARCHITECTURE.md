# Agent OS Architecture — Maurice's AI Empire

**Vision:** Build the thing that builds things. An operating system where every agent, tool, library, and loop is connected like neurons in a brain. Completed code releases dopamine. The system gets addicted to shipping.

---

## 1. The Neural Metaphor

| Biological System | Digital Equivalent | Implementation |
|---|---|---|
| Neuron | Agent / Skill / Tool | Hermes agent, Claude skill, OpenClaw tool |
| Axon | Message bus / event pipe | `state/neural-bus/` JSON events |
| Synapse | MCP / API / webhook | Hermes ↔ OpenClaw, GitHub Actions, Telegram |
| Neurotransmitter | Dopamine signal | `state/dopamine/score.json` + reward hook |
| Reward circuit | Completed code → pleasure signal | `ops/cron/24-dopamine-score.sh` |
| Memory (short-term) | Session / working memory | `memory/CURRENT.md`, Claude context |
| Memory (long-term) | Skills + libraries | `.skills/`, `09_LIBRARY/`, `state/libraries/` |
| Plasticity | Self-improvement loop | `loop/run_loop.sh`, `ops/cron/21-loop-improve.sh` |
| Reflex arc | Silver loop | Fixed trigger → fixed action, no reasoning delay |

## 2. Dopamine Mechanics

### The Biochemical Loop
1. **Action** → neuron fires
2. **Result** → outcome measured
3. **Reward** → dopamine released if outcome > threshold
4. **Reinforcement** → pathway strengthened
5. **Habit** → loop becomes automatic

### The Digital Loop
1. **Agent completes task** → code/test/commit/merge
2. **Validator measures** → tests pass, file changed, commit created
3. **Dopamine emitted** → `state/dopamine/score.json` incremented
4. **Skill strengthened** → lesson written to `loop/lessons.json`
5. **Silver loop formed** → task becomes cron-triggered reflex

### Dopamine Score Formula
```
dopamine_delta = (lines_of_code * 0.1) + (tests_passed * 2) + (commits * 1) + (merged_prs * 5) + (new_skill * 10) + (library_entry * 3) + (revenue_event * 50)
```

Daily decay: `current_score *= 0.95` (forgetting curve)

## 3. Agent Hierarchy

```
                    ┌─────────────────┐
                    │  EMPEROR AGENT  │
                    │  (Orchestrator) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
   │ RESEARCH│          │ BUILD   │         │ GTM     │
   │ AGENT   │          │ AGENT   │         │ AGENT   │
   └────┬────┘          └────┬────┘         └────┬────┘
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
   │ GitHub  │          │ Engineer│         │ Sales   │
   │ Library │          │ CTO     │         │ Writer  │
   │ Skill   │          │ Spec    │         │ YouTube │
   │ Index   │          │ Agent   │         │ Operator│
   └─────────┘          └─────────┘         └─────────┘
```

### Emperor Agent
- Decides which sub-agent runs
- Reads `state/dopamine/score.json`
- Writes `state/neural-bus/emperor_decisions.json`
- Trigger: morning queue, dopamine dip, manual command

### Research Agent
- Crawls GitHub, Hacker News, AI Twitter, arXiv, model repos
- Writes `state/libraries/daily_ingest_YYYY-MM-DD.json`
- Feeds: `09_LIBRARY/`, `state/skills/candidates/`, `04_OUTPUT/GOLD_NUGGETS/`

### Build Agent
- Takes specs from Emperor
- Spawns Engineer/CTO/Spec agents
- Emits dopamine on commit/merge

### GTM Agent
- Takes shipped products
- Spawns Sales, Writer, YouTube Operator
- Emits dopamine on revenue or qualified lead

## 4. Silver Loops

Silver loops are **fixed, fast, no-decision reflexes** wired into the agent harness.

### Definition
- Trigger condition is deterministic
- Action is scripted
- No LLM reasoning in the hot path
- Can call an LLM only in a safe subprocess

### Installed Silver Loops

| # | Name | Trigger | Action | File |
|---|---|---|---|---|
| 01 | Morning Queue | 06:00 cron | Rank tasks, dispatch agents | `ops/cron/06-ceo-daily-goals.sh` |
| 02 | Tech Health | 06:15 cron | Check git, disk, secrets | `ops/cron/07-cto-tech-health.sh` |
| 03 | Ship Loop | 07:00 cron | Engineer runs backlog | `ops/cron/08-engineer-ship.sh` |
| 04 | Research Ingest | 08:00 cron | Scrape AI sources → libraries | `ops/cron/22-research-ingestion.sh` |
| 05 | Library Sync | 08:30 cron | Sync indices, skills, manifests | `ops/cron/23-library-sync.sh` |
| 06 | Dopamine Score | 09:00 cron | Score yesterday's output | `ops/cron/24-dopamine-score.sh` |
| 07 | Neural Broadcast | 09:15 cron | Push state to OpenClaw/Hermes | `ops/cron/25-neural-broadcast.sh` |
| 08 | Backup Health | 18:00 cron | Archive + integrity check | `ops/cron/19-ops-backup-health.sh` |
| 09 | Daily Review | 20:00 cron | Retro + lessons | `ops/cron/20-loop-review.sh` |
| 10 | Self-Improve | 20:30 cron | Patch loops from lessons | `ops/cron/21-loop-improve.sh` |

## 5. Libraries

### GitHub Library (`09_LIBRARY/`)
- Cloned open-source repos
- `MANIFEST.md` tracks purpose + status
- `update-all.sh` pulls all repos
- `.indices/` holds generated metadata

### Skill Library
- `.skills/` per project
- `~/.codex/skills/`, `~/.hermes/skills/`
- `state/skills/registry.json` unified index

### Knowledge Library
- `04_OUTPUT/GOLD_NUGGETS/`
- `04_OUTPUT/CLAUDE_EXPORT/`
- `07_WIKI/`
- `09_LIBRARY/.indices/`

### Dopamine Library
- `state/dopamine/history.json` — daily scores
- `state/dopamine/reward_map.json` — which actions yield how much
- `state/dopamine/streak.json` — consecutive shipping days

## 6. Neural Bus

All events flow through `state/neural-bus/` as JSON.

```json
{
  "ts": "2026-06-30T08:15:00Z",
  "type": "code.completed",
  "source": "engineer_agent",
  "payload": {
    "repo": "hermes-archi",
    "commit": "abc1234",
    "files": 3,
    "tests": 5,
    "dopamine_delta": 12.3
  },
  "recipients": ["openclaw", "hermes", "dashboard"]
}
```

Subscribers:
- Hermes: updates memory, routes next task
- OpenClaw: shows notification, logs to dashboard
- Dashboard: updates live charts
- Dopamine scorer: adds to score

## 7. OpenClaw Integration

OpenClaw is the **local limbic system** — fast reflexes, tools, UI.

- Hermes sends commands to OpenClaw via MCP
- OpenClaw returns tool results into the neural bus
- OpenClaw dashboard shows dopamine + active loops
- OpenClaw mobile (when paired) gets push notifications

## 8. Daily Flow

```
06:00  Morning Queue        → Emperor decides today's targets
06:15  Tech Health          → System checks
07:00  Ship Loop            → Engineer builds
08:00  Research Ingest      → New repos, papers, tools discovered
08:30  Library Sync         → Indices updated
09:00  Dopamine Score       → Yesterday's reward computed
09:15  Neural Broadcast     → All systems informed
...    User works with agents
18:00  Backup Health        → Archive
20:00  Daily Review         → Retro
20:30  Self-Improve         → Patch silver loops
```

## 9. Success Metric

The Agent OS is working when:
- Every completed task emits a dopamine signal
- Research automatically fills libraries every day
- Skills get stronger from lessons
- OpenClaw, Hermes, Claude Code share the same memory
- Maurice ships more with less manual routing
