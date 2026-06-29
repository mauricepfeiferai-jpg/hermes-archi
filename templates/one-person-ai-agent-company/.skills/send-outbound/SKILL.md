---
name: send-outbound
description: Draft personalized outbound messages for warm leads.
when_to_use: When Sales Agent runs at 11:00 or before manual outreach.
---

# Send Outbound

## Inputs

- `sales/crm.json`
- `researcher/outputs/daily_brief_*.md`
- Previous `sales/outputs/outbound_draft_*.md`

## Output

- `sales/outputs/outbound_draft_YYYY-MM-DD.md`

## Definition of Done

- [ ] 3 personalized outbound messages drafted
- [ ] Each references a specific observation about the lead
- [ ] Soft ask, no hard pitch
- [ ] Human approval required before sending
