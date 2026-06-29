# System Prompts Leaks — Analysis Summary

## Source
https://github.com/asgeirtj/system_prompts_leaks

## Repo Structure
- Anthropic/Claude Code bundled skills (run, verify, review, deep-research, loop, etc.)
- OpenAI/Codex prompts with personality placeholders
- Google/Gemini, Meta, Microsoft, xAI, Perplexity, Qwen, Notion, Cursor, Mistral

## Key Patterns Found

### 1. Skill Format (Claude Code)
```yaml
---
name: run-skill-generator
description: Teach /run and /verify how to build and launch your project...
---
```
Skills are short, frontmatter-driven, and point at a driver script.

### 2. Driver + Skill Pair
```
.claude/skills/run-<unit>/
  SKILL.md      ← short agent instructions
  driver.mjs    ← executable harness
```
This is a best practice: prose points to code that actually runs.

### 3. Definition of Done
Claude Code skills demand evidence:
- Launch the actual app in the container
- Take a screenshot if GUI
- Commit the interaction harness
- Every command in SKILL.md must have been run successfully

### 4. Personality Placeholders
OpenAI Codex uses `{{ personality }}` templating for different tones.

### 5. Tool Lists
Claude Code system prompt includes explicit tool catalog:
- Agent, Bash, Edit, Read, Skill, Workflow, Write, AskUserQuestion, etc.

## Applications to AI Empire
- Adopt `name/description/when_to_use` frontmatter for Hermes skills
- Pair every skill with a driver script / verification command
- Add "Definition of Done" to each agent job description
- Use personality templates for writer/sales/outreach agents
- Build a skill registry with tool listings

## Status
Isolated analysis complete. Cloned repo removed. Findings saved.
