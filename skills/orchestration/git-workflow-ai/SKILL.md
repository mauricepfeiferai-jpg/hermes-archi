---
name: git-workflow-ai
title: Git Workflow for AI Workspaces — Three Repos, One Rhythm
description: "Hermes orchestration skill for managing AI workspace assets (CLAUDE.md, skills, eval criteria, autoresearch) with Git. Based on Aakash Gupta / Shubham Saboo three-repo model. Never auto-deletes, auto-publishes, pushes git, or changes production without approval."
version: 1.0.0
author: AI Empire
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Git, Version-Control, AI-Workspace, CLAUDE.md, Skills, Eval, PM-OS]
    category: orchestration
    requires_toolsets: [terminal, file]
---

# Git Workflow for AI Workspaces

Use this skill whenever AI workspace assets change: CLAUDE.md, skills, eval criteria, autoresearch configs, project planning docs.

Core rule:

> pull → branch → edit → commit → push → PR → merge

## The Three Repos

| Repo | Holds | Example Paths |
|---|---|---|
| **Repo 1 — Private Workspace** | Personal CLAUDE.md, private skills, autoresearch configs | `~/.claude/`, `~/.codex/skills/`, `~/.hermes/` |
| **Repo 2 — Shared Tools** | Skills/templates without personal context | `pm-skills`, `karpathy-guidelines`, `skill-picker` |
| **Repo 3 — Per-Project** | PLANNING.md, eval criteria, code, full build record | `hermes-archi`, `andrej-karpathy-skills` |

## Daily Rhythm (Claude Code natural language)

1. **Pull:** "Pull the latest changes from main."
2. **Branch:** "Create a new branch called improve/prd-reviewer-v7." (skip for solo private workspace)
3. **Edit:** Update skill, CLAUDE.md, eval criteria.
4. **Commit:** "Commit my changes with the message: add behavior contract check to PRD reviewer."
5. **Push:** "Push my changes."
6. **PR:** "Open a pull request." (shared repos)
7. **Merge:** Merge after review.

## Four Workflows

### Skill Rollback

```text
When a skill edit makes outputs worse:
1. git log --oneline skills/prd-reviewer/SKILL.md
2. git revert [bad-commit-hash]
3. Verify output with old version.
```

### CLAUDE.md Pruning

```text
Once per month:
1. Count lines: wc -l CLAUDE.md
2. If >200 lines, diff last month: git diff HEAD@{30.days.ago} -- CLAUDE.md
3. Cut drift: remove duplicated, outdated, or ignored instructions.
4. Commit: "prune CLAUDE.md: remove outdated provider routing and duplicate rules"
```

### Autoresearch Logging

```text
For each experiment run:
1. Branch: experiment/agent-loop-v3
2. Run 100 iterations overnight.
3. Each iteration: commit if score improves, revert if score drops.
4. Morning: git log --oneline is the experiment log.
```

### Eval Versioning

```text
When score changes:
1. git log -- evals/
2. Check whether the eval scoring function or the model/prompt changed.
3. git diff [commit] -- evals/score.py
```

## Security Checklist

Before pushing any workspace repo:

- [ ] Remove API keys and `.env` files (use `.gitignore`)
- [ ] Remove customer names, internal strategy, HR/performance data
- [ ] Remove raw Slack exports and sensitive screenshots
- [ ] Run a secret scan: `detect-secrets scan` or `git-secrets`
- [ ] Confirm repo is private if it contains personal context

## Templates

- `assets/04_TEMPLATES/GIT_RHYTHM_PROMPT.md` — daily loop prompt
- `assets/04_TEMPLATES/CLAUDE_MD_PRUNE_PROMPT.md` — monthly pruning prompt
