# AI Empire Insights — 2026-06-29

Dokumentation der in dieser Session extrahierten Gold Nuggets und ihrer Integration in `hermes-archi`.

## Gold Nuggets

| Nugget | Datei | Bedeutung |
| GitHub AI Workspace Memory | [gold-nuggets/GOLD_GITHUB_AI_WORKSPACE_MEMORY_THREE_REPOS_2026-06-29.md](gold-nuggets/GOLD_GITHUB_AI_WORKSPACE_MEMORY_THREE_REPOS_2026-06-29.md) | Drei Repos als AI-Gedächtnis |
|---|---|---|
| Multi-Subagent Fan-Out | [gold-nuggets/GOLD_HERMES_MULTI_SUBAGENT_FAN_OUT_2026-06-29.md](gold-nuggets/GOLD_HERMES_MULTI_SUBAGENT_FAN_OUT_2026-06-29.md) | Parallele Agenten → Cross-Verify → Merge |
| Chinese AI Stack 87% Cost Cut | [gold-nuggets/GOLD_AI_STACK_CHINESE_MODELS_87_PERCENT_COST_CUT_2026-06-29.md](gold-nuggets/GOLD_AI_STACK_CHINESE_MODELS_87_PERCENT_COST_CUT_2026-06-29.md) | Task-basiertes Routing auf chinesische Primaries |
| One-Person AI Agent Company | [gold-nuggets/GOLD_ONE_PERSON_AI_AGENT_COMPANY_2026-06-29.md](gold-nuggets/GOLD_ONE_PERSON_AI_AGENT_COMPANY_2026-06-29.md) | 7 Agents, 10 Cron Jobs, 0 Employees |

## Produkte / Templates

- `templates/one-person-ai-agent-company/` — Starter-Struktur für eine Solo-AI-Agent-Company.
- `skills/orchestration/swarm-fan-out/` — Hermes Swarm Fan-Out Skill.
- `control-plane/hermes/config/model-policy.env.template` — Chinese-Stack-Routing-Template.

## Model-Routing (Chinese Stack)

Template liegt unter `control-plane/hermes/config/model-policy.env.template`.

```env
HERMES_TASK_REASONING_PRIMARY=kimi-k2.7
HERMES_TASK_REASONING_FALLBACK=claude-opus-4-6

HERMES_TASK_CODE_PRIMARY=qwen-3.7-max
HERMES_TASK_CODE_FALLBACK=gpt-5.5

HERMES_TASK_AGENT_LOOP_PRIMARY=glm-5.2
HERMES_TASK_AGENT_LOOP_FALLBACK=claude-sonnet-4-7

HERMES_TASK_BULK_PRIMARY=mimo-v2.5
HERMES_TASK_BULK_FALLBACK=gpt-5.5-mini

HERMES_TASK_IMAGE_PRIMARY=wan-2.5
HERMES_TASK_IMAGE_FALLBACK=gpt-image-2

HERMES_TASK_VIDEO_PRIMARY=kling-3.0
HERMES_TASK_VIDEO_FALLBACK=sora-2
```

## Nächste Schritte (im Projekt)

1. Drei-Repo-Struktur für AI Empire definieren (Private Workspace, Shared Tools, Per-Project).
2. `control-plane/hermes/runtime/main.py` um Swarm-Run-Orchestration erweitern.
2. `model-layer/orchestrator.ts` um task-basiertes Chinese-Primary-Routing erweitern.
3. `control-plane/hermes/cron/` um 10 Company-Cron-Jobs als Templates anlegen.
4. Review/Retro/Loop-Integration mit `self-improvement-100x-loop` verbinden.
5. Git diff reviewen; commit/push nur nach Approval.

## Letzte Aktualisierung

2026-06-29 19:12

## Productized Template

- `products/one-person-ai-agent-company/` — Landing page, pricing, sales copy for the top-scoring viral product.

## Go-to-Market

- Marc Lou First-Customer Strategien als Gold Nugget gespeichert.
- 14-Tage-Launch-Plan, Cold-Outreach-Templates und Lead-Magnet-Plan fuer One-Person AI Agent Company erstellt.

## Shipping Manifest

- Paradigmenwechsel: Ship everything, test everything, monetize everything.
- Execution Dashboard fuer Sprint 2026-W27 erstellt.

## 5 Viral Products Packaged

- Hermes Swarm Fan-Out Skill
- Chinese AI Stack Migration Playbook
- Git Workflow for AI Workspaces
- Self-Improvement 100x Loop
- Karpathy Agent OS Starter Kit (early access)
All with PRODUCT.md, landing pages, pricing, checkout templates.

## Product Factory

- `products/ai-empire-product-factory/` — Meta-system that turns Gold Nuggets into shippable products.

## Agent Reach Integration

- Agent Reach staged for security review.
- Integration skill + plan created.
- Next: isolated evaluation in dedicated venv.

## Production Mode

- Production runbook created for One-Person AI Agent Company Template.
- 100x window loop monitor defined for 5 tmux windows.
- Status: GOING LIVE.
