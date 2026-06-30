#!/bin/bash
# Silver Loop L2: PR Babysitter (assisted, human gate)
# Checks open PRs, summarizes them, suggests review actions. No auto-merge.
set -euo pipefail
REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUT="$REPO/state/pr-babysitter/report_${DATE}_${TIME}.json"
mkdir -p "$REPO/state/pr-babysitter"
python3 - "$REPO" "$OUT" "$DATE" "$TIME" <<PYTHON
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

repo, outfile, date, time = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=repo)
        return {"rc": r.returncode, "out": r.stdout[-2000:], "err": r.stderr[-500:]}
    except Exception as e:
        return {"rc": -1, "error": str(e)}

# Fetch PRs using gh CLI (assumes auth)
pr_list = run("gh pr list --json number,title,author,headRefName,baseRefName,createdAt,url --limit 10")
prs = []
if pr_list["rc"] == 0:
    try:
        prs = json.loads(pr_list["out"])
    except Exception:
        pass

verifier_notes = []
for pr in prs:
    # Independent verifier: check if branch has passing tests / lint
    number = pr.get("number")
    checks = run(f"gh pr checks {number} --json name,state")
    pr["checks_summary"] = checks["out"]
    pr["verdict"] = "needs_human_review"  # L2 never auto-merges
    verifier_notes.append({"pr": number, "verdict": pr["verdict"]})

report = {
    "date": date,
    "time": time,
    "source": "pr-babysitter.sh",
    "level": "L2",
    "prs_found": len(prs),
    "prs": prs,
    "verifier_notes": verifier_notes,
    "human_gate": True,
    "auto_merge": False,
    "suggested_actions": [
        "Review PRs with failing checks first",
        "Approve PRs with all green checks",
        "Never merge without human approval"
    ]
}
outfile.write_text(json.dumps(report, indent=2))

bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc)
event = {
    "ts": now.isoformat().replace("+00:00", "Z"),
    "type": "pr.babysitter.report",
    "source": "pr-babysitter.sh",
    "payload": report,
    "recipients": ["emperor", "cto", "openclaw_main"]
}
ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
(bus_dir / f"{ts}_pr.babysitter.report.json").write_text(json.dumps(event, indent=2))
print(f"PR Babysitter: {len(prs)} PRs, report: {outfile}")
PYTHON
