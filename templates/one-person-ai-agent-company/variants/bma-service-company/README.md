# BMA Service Business Variant

Adaptation of the One-Person AI Agent Company for German fire-safety contractors (Brandmeldeanlagen).

## Roles

| AI Agent | Real-World Job |
|---|---|
| PM | Project manager for inspections, deadlines, customer appointments |
| Compliance | VdS / DIN / local authority documentation + audit prep |
| Field Engineer | Site visit prep, report templates, material lists |
| Customer Success | Follow-ups, reminders, review collection, upsell |
| Ops | Backup, scheduling, tool health |
| Loop | Review errors, missed deadlines, compliance gaps |

## Key Differences
- CRM is customer/project-based, not lead-based
- Compliance agent owns VdS/Feuerwehr deadlines
- Field engineer pre-fills inspection reports before site visits
- Customer success triggers recurring maintenance upsells

## Schedule
- 06:00 PM: daily project priorities
- 06:30 Compliance: audit deadlines
- 07:00 Field Engineer: site visit prep
- 08:00 Customer Success: follow-ups
- 18:00 Ops: backup + health
- 20:00 Loop: review + patch
