# One-Person AI Agent Company — Live Dashboard

## How to view

### Option 1: One-click launcher (recommended)
Double-click `launch_dashboard.command` (macOS) or run:

```bash
./launch_dashboard.sh
```

This starts a local HTTP server on the next free port (starting at 8777) and opens the dashboard in your default browser. The server keeps running as long as the Terminal window stays open.

### Option 2: Open directly
Double-click `index.html` or open it in any browser:

```
file:///Users/maurice/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company/dashboard/index.html
```

`data.json` is embedded at build time and the key numbers are pre-filled into the HTML, so the dashboard loads without a server and still shows live data.

### Option 3: Serve fresh data manually
Run the local server to fetch the latest `data.json`:

```bash
cd templates/one-person-ai-agent-company/dashboard
./serve.sh
```

Then open http://localhost:8080

## Regenerate data

```bash
cd templates/one-person-ai-agent-company/dashboard
python3 generate_data.py
python3 build_standalone.py
```

## Files

| File | Purpose |
|------|---------|
| `index.html` | Standalone dashboard (data embedded + pre-filled) |
| `data.json` | Live dashboard data |
| `generate_data.py` | Collect live system metrics |
| `build_standalone.py` | Embed data.json into index.html and pre-fill DOM values |
| `serve.sh` | Local HTTP server |
| `launch_dashboard.command` | macOS one-click launcher (server + browser) |
| `launch_dashboard.sh` | Shell launcher (server + browser) |
| `dashboard-preview.png` | Static screenshot |

## Troubleshooting

**Dashboard opens but shows only zeros / no data**
- Run `python3 build_standalone.py` to rebuild `index.html` from the latest `data.json`.
- Use the launcher instead of opening `index.html` directly.

**"Nothing happens" when double-clicking `index.html`**
- Use `launch_dashboard.command` — some browsers restrict `file://` pages from fetching fresh data.
