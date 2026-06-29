---
name: run-morning-queue
description: Execute the CEO Agent's ranked morning action queue for today.
when_to_use: At the start of every workday, after the CEO Agent has produced morning_queue_YYYY-MM-DD.md.
---

# Run Morning Queue

1. Read `ceo/outputs/morning_queue_YYYY-MM-DD.md`
2. For each ranked action:
   - Run the named skill or script
   - Verify the expected output file exists
   - Stop on error and flag for human review
3. Write `ops/outputs/queue_status_YYYY-MM-DD.md`

## Driver

```bash
bash .skills/run-morning-queue/driver.sh
```

## Definition of Done

- [ ] All queue items ran or were explicitly skipped
- [ ] Each expected output file exists in `*/outputs/`
- [ ] Errors are logged, not ignored
- [ ] Status report written to `ops/outputs/queue_status_*.md`
