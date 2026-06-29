---
name: run-agent
description: Run a single agent role task through the dispatcher.
when_to_use: When a specific agent needs to produce its daily output or when called by the morning queue.
---

# Run Agent

## Usage

```bash
bash .skills/run-agent/driver.sh {agent} {task} {date}
```

Examples:

```bash
bash .skills/run-agent/driver.sh ceo daily-goals 2026-06-29
bash .skills/run-agent/driver.sh cto tech-health 2026-06-29
bash .skills/run-agent/driver.sh writer draft 2026-06-29
```

## Definition of Done

- [ ] Agent output file exists in `*/outputs/`
- [ ] Output matches expected template
- [ ] No destructive action executed without approval file
