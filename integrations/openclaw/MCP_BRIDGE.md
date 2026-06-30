# OpenClaw MCP Bridge — Agent OS Integration

## Role
OpenClaw is the **local limbic system** of the Agent OS: fast tools, local execution, UI, and mobile notifications.

## Connection Pattern

```
Hermes / Emperor Agent  ──MCP──▶  OpenClaw Gateway  ──▶  Tools (exec, browser, file, cron)
                              ◀── JSON result ──
                              │
                              └──▶  Mobile App (push / approval)
```

## How Hermes Uses OpenClaw

Hermes dispatches a task to OpenClaw via:

```bash
python3 agents/agent-os-harness/dispatch.py openclaw_main "run local tool" --payload '{"tool":"exec","cmd":"ls"}'
```

OpenClaw returns tool output. Hermes writes result to `state/neural-bus/`.

## How OpenClaw Reads Agent OS State

OpenClaw can read:
- `state/dopamine/score.json` → show reward score
- `state/neural-bus/*.json` → show recent events
- `state/libraries/.indices/*.json` → search libraries

## Mobile Notifications

When Agent OS emits important events:
- `code.completed` → OpenClaw mobile notification
- `dopamine.score.updated` → push: "Streak: X, Score: Y"
- `library.entry` → push: "New AI repo discovered"

## Security

- Telegram remains disabled on 16GB Mac per memory decision.
- OpenClaw exec tool runs with `security=full` and `ask=off` only for known loops.
- Unknown commands require approval.

## Pairing Status

- Gateway: `bind=lan` on `192.168.178.172:18789`
- Tailscale: `mac-mini-von-maurice.tail1ca9fd.ts.net`
- Mobile pairing: pending (requires manual App scan / setup code approval)
