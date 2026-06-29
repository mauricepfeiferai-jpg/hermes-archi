---
name: review-output
description: Review a generated output file for quality, correctness, and safety.
when_to_use: Before any output is considered final, especially before posting, committing, or sending to a customer.
---

# Review Output

## Usage

```bash
bash .skills/review-output/driver.sh path/to/output.md
```

## Checks

- Quality gates from agent job description
- No secrets, PII, or legal risk
- Tone matches brand voice
- CTA is clear and safe

## Definition of Done

- [ ] File read and evaluated
- [ ] Issues listed or "no issues found"
- [ ] Approval recommendation: APPROVE / REVISE / REJECT
- [ ] Human gets final say on production actions
