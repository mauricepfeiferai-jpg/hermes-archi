#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
LIB_DIR = REPO / "09_LIBRARY"
RANKED = REPO / "state" / "libraries" / "ranked_repos.json"
MANIFEST = LIB_DIR / "MANIFEST.md"

def main():
    if not RANKED.exists():
        print(json.dumps({"error": "ranked_repos.json missing"}))
        return

    ranked = json.loads(RANKED.read_text())
    top = [i for i in ranked.get("top_10", []) if i.get("ai_empire_score", 0) >= 10][:3]

    cloned = []
    for item in top:
        url = item.get("url", "")
        if not url.startswith("https://github.com/"):
            continue
        parts = url.rstrip("/").split("/")
        name = parts[-2] + "-" + parts[-1]
        target = LIB_DIR / name
        if target.exists():
            cloned.append({"repo": name, "status": "already_exists"})
            continue
        try:
            result = subprocess.run(["git", "clone", "--depth=1", url, str(target)], capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                cloned.append({"repo": name, "status": "cloned", "score": item.get("ai_empire_score")})
                update_manifest(name, url)
            else:
                cloned.append({"repo": name, "status": "failed", "err": result.stderr[-200:]})
        except Exception as e:
            cloned.append({"repo": name, "status": "error", "err": str(e)})

    report = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cloned": cloned,
        "total": len(cloned)
    }

    bus_dir = REPO / "state" / "neural-bus"
    bus_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    event = {
        "ts": now.isoformat().replace("+00:00", "Z"),
        "type": "library.auto_clone.completed",
        "source": "auto_clone_top_repos.py",
        "payload": report,
        "recipients": ["emperor", "researcher", "cto"]
    }
    ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
    (bus_dir / f"{ts}_library.auto_clone.completed.json").write_text(json.dumps(event, indent=2))
    print(json.dumps(report, indent=2))

def update_manifest(name, url):
    header = "# AI Empire Library Manifest\n\n| Name | Source | Purpose | Status | Size |\n|------|--------|---------|--------|------|\n"
    row = "| " + name + " | " + url + " | Auto-ranked AI agent repo | cloned | - |\n"
    if not MANIFEST.exists():
        MANIFEST.write_text(header + row)
    else:
        text = MANIFEST.read_text()
        if url not in text:
            text = text.rstrip() + "\n" + row
            MANIFEST.write_text(text)

if __name__ == "__main__":
    main()
