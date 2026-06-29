# Spec Agent

The Spec Agent writes implementation specs for tasks that are too complex or ambiguous to one-shot.

## Output Files

- `specs/{task-id}/PRODUCT.md` — product behavior
- `specs/{task-id}/TECH.md` — tech architecture
- `specs/{task-id}/DECISION_LOG.md` — open decisions (optional)

## How to Use

1. Label a task `ready-to-spec` in `engineer/backlog/` or GitHub.
2. Run the Spec Agent:
   ```bash
   bash ops/cron/13-spec-agent.sh {task-id}
   ```
3. Review the spec files.
4. Either:
   - Approve → label `ready-to-implement`
   - Reject → add comments, relabel `needs-info`

## Integration with Engineer Agent

The Engineer Agent checks for a spec before implementing:

```bash
if [ -f "specs/$TASK_ID/PRODUCT.md" ] && [ -f "specs/$TASK_ID/TECH.md" ]; then
  # Implement according to spec
else
  # One-shot or ask for spec
fi
```
