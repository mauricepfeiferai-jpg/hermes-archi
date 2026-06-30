# Loop Configuration — AI Empire / Hermes-Archi

## Active Loops

| Pattern | Cadence | Status | Command |
|---------|---------|--------|---------|
| Daily Triage | 1d | L1 report-only | Read memory, surface next actions |
| Launch Monitor | 1h | L1 | Watch PayPal / traffic / engagement |
| Dependency Sweeper | 1w | L1 | Check npm/pip CVEs, report only |

## Human Gates

- No auto-merge on main
- No payment processing automation until first 10 manual sales
- No auto-post on social accounts
- All product releases require human approval

## Budget

- Max tokens/day: 200k
- Kill switch: `loop-pause-all` flag in STATE.md
- Estimate: `npx @cobusgreyling/loop-cost --pattern daily-triage`

## Links

- Pattern library: library/loop-engineering-cobusgreyling/patterns/
- Launch playbook: products/one-person-ai-agent-company/go-to-market/LAUNCH_PLAYBOOK.md\n