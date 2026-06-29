# Swarm Prompt Template

```text
Launch multiple sub-agents for [TASK].

Split the work into: [N angles/subtasks - or let Hermes decide]
Each agent should: work independently, then report back in the agreed format.
Cross-verify: have agents check each other's findings before you finalize.
Merge into: [ONE clean output - report / code / summary / decision]

Work autonomously. Report back when all agents are done.
```

## Examples

Research:
```text
Launch multiple sub-agents to research "AI-agentenbasierte Angebotserstellung fuer BMA-Dienstleister" from 4 different angles: market, technology, workflow, and regulation. Merge into one report with actionable next steps.
```

Coding:
```text
Launch multiple sub-agents to build a contact form feature: one on backend API + validation, one on frontend HTML/JS, one on tests. Cross-verify interfaces, then merge into a single implementation plan with file changes.
```

Debugging:
```text
Launch multiple sub-agents to investigate why the Hermes gateway occasionally returns 503. Use hypotheses: provider routing, port conflict, launchd misconfig, memory pressure. Converge on the most likely root cause.
```

Content:
```text
Launch 3 sub-agents to draft a LinkedIn post about the AI Empire Agent-OS in different tones: professional, punchy, story-driven. Pick the strongest and merge the best elements into one final post.
```
