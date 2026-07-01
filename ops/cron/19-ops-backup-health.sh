#!/bin/bash
# Silver Loop: Backup Health
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
cd "$REPO"
source .venv/bin/activate
REPO="$HOME/ai-empire/projects/hermes-archi"
ARCHIVE="$REPO/03_ARCHIVE/backup/$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE"
python3 - "$REPO" "$ARCHIVE" <<PYTHON
import json, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
repo, archive = Path(sys.argv[1]), Path(sys.argv[2])

state_src = repo / "state"
memory_src = Path.home() / ".openclaw" / "workspace" / "ai-empire" / "memory"

copied = 0
for src in [state_src, memory_src]:
    if not src.exists():
        continue
    for f in src.rglob("*"):
        if f.is_file() and ".venv" not in f.parts and "node_modules" not in f.parts and ".git" not in f.parts:
            rel = f.relative_to(src)
            dst = archive / src.name / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            copied += 1

report = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "source": "19-ops-backup-health.sh",
    "archive_path": str(archive),
    "files_copied": copied,
}
(archive / "backup_report.json").write_text(json.dumps(report, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "ops.backup.completed",
    "source": "19-ops-backup-health.sh",
    "payload": report,
    "recipients": ["emperor", "cto", "openclaw_main"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_ops.backup.completed.json").write_text(json.dumps(event, indent=2))
print(f"Backup health: {copied} files archived")
PYTHON
# Update handoff after loop
python3 "$REPO/control-plane/hermes/handoff_generator.py" <<EOF_H
19-ops-backup-health.sh: completed $(date +%Y-%m-%d-%H:%M)
EOF_H
