#!/bin/bash
# Silver Loop: CTO Tech Health
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUT="$REPO/state/cto/tech_health_${DATE}.json"
mkdir -p "$REPO/state/cto"
python3 - "$REPO" "$OUT" <<PYTHON
import json, subprocess, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
repo, outfile = Path(sys.argv[1]), Path(sys.argv[2])

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=repo)
        return {"rc": r.returncode, "out": r.stdout[-500:], "err": r.stderr[-300:]}
    except Exception as e:
        return {"rc": -1, "error": str(e)}

git_status = run("git status --short")
branch = run("git branch --show-current")["out"].strip() or "main"
disk = shutil.disk_usage(repo)
secrets = run("grep -RInE \x27API_KEY|SECRET|TOKEN|PRIVATE\x27 --exclude-dir=.git --exclude-dir=.venv --exclude=\x27*.md\x27 . | head -20")
python_ok = run("python3 -c \x27import sys; print(sys.version_info[:2])\x27")
node_ok = run("node --version")

health = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "time": datetime.now().strftime("%H:%M"),
    "source": "07-cto-tech-health.sh",
    "branch": branch,
    "git_dirty": len(git_status["out"].strip()) > 0,
    "disk_gb_free": round(disk.free / 1e9, 2),
    "disk_gb_total": round(disk.total / 1e9, 2),
    "secrets_scan_hits": len(secrets["out"].strip().splitlines()) if secrets["out"].strip() else 0,
    "python_ok": python_ok["rc"] == 0,
    "node_ok": node_ok["rc"] == 0,
    "alerts": [],
}
if health["git_dirty"]:
    health["alerts"].append("Uncommitted changes present")
if disk.free < 5e9:
    health["alerts"].append("Disk space below 5GB")
if health["secrets_scan_hits"] > 0:
    hits = health["secrets_scan_hits"]
    health["alerts"].append(f"{hits} potential secret hits")

outfile.parent.mkdir(parents=True, exist_ok=True)
outfile.write_text(json.dumps(health, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "cto.tech_health",
    "source": "07-cto-tech-health.sh",
    "payload": health,
    "recipients": ["emperor", "cto", "openclaw_main"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_cto.tech_health.json").write_text(json.dumps(event, indent=2))
alerts_count = len(health["alerts"])
print(f"CTO tech health: {outfile}, alerts={alerts_count}")
PYTHON
