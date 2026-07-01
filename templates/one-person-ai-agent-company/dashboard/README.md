# One-Person AI Agent Company — Live Dashboard

## How to view

### Option 1: Open directly (works now)
Double-click `index.html` or open it in any browser:

```
file:///Users/maurice/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company/dashboard/index.html
```

`data.json` is embedded at build time, so the dashboard loads without a server.

### Option 2: Serve fresh data
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
| `index.html` | Standalone dashboard (data embedded) |
| `data.json` | Live dashboard data |
| `generate_data.py` | Collect live system metrics |
| `build_standalone.py` | Embed data.json into index.html |
| `serve.sh` | Local HTTP server |
| `dashboard-preview.png` | Static screenshot |
