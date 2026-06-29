---
name: swarm-fan-out
title: Swarm Fan-Out — One Prompt, Parallel Agents, One Clean Answer
description: "Hermes orchestration skill for fanning out a task across multiple parallel subagents, cross-verifying their outputs, and merging into one clean result. Use for research, coding, debugging, content drafting, or any task that benefits from multiple independent angles. Never auto-deletes, auto-publishes, pushes git, or changes production without approval."
version: 1.0.0
author: AI Empire
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Swarm, Subagents, Fan-Out, Parallel, Cross-Verification, Merge, Orchestration]
    category: orchestration
    requires_toolsets: [terminal, file]
---

# Swarm Fan-Out

Use this skill whenever one task is better solved by a small team of parallel agents than by a single agent walking step-by-step.

Core rule:

> Fan out → cross-verify → merge → one clean answer.

German operating rule:

> Ein Prompt spannt das Team auf; die Verifikation liefert die Qualitaet; das Merge liefert das Ergebnis.

## When to use

- Research from multiple angles.
- Code split across backend / frontend / tests / docs.
- Debugging with competing hypotheses.
- Content drafted in multiple tones, then pick/merge the strongest.
- Any task where independent agents reduce bias and catch blind spots.

## Trigger phrases

- "Launch multiple sub-agents for [task]."
- "Hermes, swarm this: [task]."
- "Fan out [N] agents for [task] and merge."

## Runtime state

Write run artifacts to:

`/tmp/empire-os/state/swarm/`

Required files per run:

- `SWARM_BRIEF.md` — task, angles, agents
- `AGENT_OUTPUTS.json` — one entry per agent
- `CROSS_VERIFICATION.md` — checks, conflicts, resolutions
- `MERGED_OUTPUT.md` — final clean answer
- `RUN_RETROSPECTIVE.md` — what worked, what to improve

## Standard flow

1. **Brief the swarm**
   - Task
   - Number of agents / angles
   - Output format per agent
   - Merge target format

2. **Launch agents in parallel**
   - Each agent gets its own angle/subtask
   - Each agent works independently
   - Each agent reports back in the agreed format

3. **Cross-verify**
   - Agents check each other's findings
   - Flag conflicts, contradictions, gaps
   - Resolve or mark unresolved for human decision

4. **Merge**
   - Produce one clean output
   - Cite source agents (Agent A, Agent B, ...)
   - Preserve dissenting notes if relevant

5. **Retrospect**
   - Log to `RUN_RETROSPECTIVE.md`
   - Feed into `self-improvement-100x-loop`

## Constraints

- Do not auto-enable skills, install packages, or restart services.
- Do not auto-delete, auto-publish, or push git.
- If agents disagree on a material fact, ask the user before finalizing.
- Keep outputs deterministic where possible: JSON schema, hooks, templates.

## Templates

- `assets/04_TEMPLATES/SWARM_PROMPT.md` — copy-paste prompt
- `assets/04_TEMPLATES/SWARM_MERGE_TEMPLATE.md` — merge output scaffold
