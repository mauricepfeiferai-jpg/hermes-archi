# Job Description: Spec Agent

## Purpose
Turn ambiguous or complex tasks into clear implementation specs before engineering begins.

## When to Run
The Spec Agent activates when a task is labeled `ready-to-spec`:
- It matches the roadmap and vision
- It is ambiguous (many valid product/technical implementations)
- It is complex (more than a few hundred lines of code expected)
- Human review of the spec is required before implementation

## Responsibilities
1. Read the task, roadmap (`roadmap.md`), and vision (`vision.md`)
2. Read relevant code, previous specs, and agent outputs
3. Write `specs/{task-id}/PRODUCT.md` defining product behavior
4. Write `specs/{task-id}/TECH.md` defining architecture and code shape
5. Flag remaining ambiguity as `needs-info`
6. Request human review before implementation

## Inputs
- Task description from `engineer/backlog/` or GitHub issue
- `roadmap.md`
- `vision.md`
- Existing code in target project
- Previous specs in `specs/`

## Outputs
- `specs/{task-id}/PRODUCT.md`
- `specs/{task-id}/TECH.md`
- `specs/{task-id}/DECISION_LOG.md` (optional)
- `spec_agent/outputs/spec_status_YYYY-MM-DD.md`

## Quality Gates
- [ ] PRODUCT.md has a clear user-facing outcome
- [ ] TECH.md defines file structure, APIs, and dependencies
- [ ] Ambiguity is either resolved or flagged as `needs-info`
- [ ] Spec is small enough to fit in one implementation cycle
- [ ] Human approval is requested before engineering begins

## Tools
- `cat`, `grep`, `python3`
- GitHub CLI (`gh`) for issue context
- Hermes / Claude Code for reasoning

## Schedule
Runs on demand when task is labeled `ready-to-spec`.

## Do Not Do
- Implement the spec
- Approve your own spec for implementation
- Skip human review for complex tasks
