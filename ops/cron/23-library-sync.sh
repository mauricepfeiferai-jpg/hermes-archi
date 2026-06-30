#!/bin/bash
# Silver Loop: Library Sync
# Rebuilds indices for skills, GitHub repos, and knowledge libraries.

set -euo pipefail

REPO="$HOME/ai-empire/projects/hermes-archi"
DATE=$(date +%Y-%m-%d)
INDEX_DIR="$REPO/state/libraries/.indices"
SKILL_DIR="$REPO/state/skills"

mkdir -p "$INDEX_DIR" "$SKILL_DIR"

echo "📚 Syncing GitHub library index..."
python3 - "$REPO" "$INDEX_DIR" <<PY
import json, sys
from pathlib import Path

repo, idx_dir = Path(sys.argv[1]), Path(sys.argv[2])
lib_dir = repo / "09_LIBRARY"
manifest = lib_dir / "MANIFEST.md"

repos = []
if manifest.exists():
    for line in manifest.read_text().splitlines():
        if line.startswith("|") and "https://github.com" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                repos.append({
                    "name": parts[2],
                    "source": parts[3],
                    "purpose": parts[4],
                    "status": parts[5] if len(parts) > 5 else "unknown",
                    "size": parts[6] if len(parts) > 6 else "-"
                })

(repo_dir := repo / "09_LIBRARY" / ".indices").mkdir(parents=True, exist_ok=True)
(repo_dir / "github_library_index.json").write_text(json.dumps({"count": len(repos), "repos": repos}, indent=2))
print(f"Indexed {len(repos)} repos")
PY

echo "🧠 Syncing skill registry..."
python3 - "$REPO" "$HOME" "$SKILL_DIR" <<PY
import json, sys
from pathlib import Path

repo, home, skill_state = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
skill_roots = [
    home / ".codex" / "skills",
    home / ".claude" / "skills",
    home / ".hermes" / "skills",
    home / ".openclaw" / "workspace" / "skills",
    repo / ".skills",
    repo / "templates" / "one-person-ai-agent-company" / ".skills",
]

skills = []
for root in skill_roots:
    if not root.exists():
        continue
    for skill_file in root.rglob("SKILL.md"):
        rel = skill_file.relative_to(root)
        skills.append({
            "name": str(rel.parent).replace("/", "_"),
            "path": str(skill_file),
            "root": str(root),
        })

skill_state.mkdir(parents=True, exist_ok=True)
(skill_state / "registry.json").write_text(json.dumps({"count": len(skills), "skills": skills}, indent=2))
print(f"Indexed {len(skills)} skills")
PY

echo "🔗 Syncing knowledge library index..."
python3 - "$REPO" "$HOME" "$INDEX_DIR" <<PY
import json, sys
from pathlib import Path

repo, home, idx_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
roots = [
    home / ".openclaw" / "workspace" / "ai-empire" / "04_OUTPUT" / "GOLD_NUGGETS",
    home / ".openclaw" / "workspace" / "ai-empire" / "04_OUTPUT" / "CLAUDE_EXPORT",
    home / ".openclaw" / "workspace" / "ai-empire" / "07_WIKI",
]

nuggets = []
for root in roots:
    if not root.exists():
        continue
    for f in root.rglob("*.md"):
        nuggets.append({"title": f.stem, "path": str(f), "root": str(root)})

(idx_dir / "knowledge_index.json").write_text(json.dumps({"count": len(nuggets), "nuggets": nuggets}, indent=2))
print(f"Indexed {len(nuggets)} knowledge nuggets")
PY

# Neural bus event
python3 - "$REPO" <<PY
import json, sys
from pathlib import Path
from datetime import datetime, timezone

repo = Path(sys.argv[1])
bus_dir = repo / "state" / "neural-bus"
bus_dir.mkdir(parents=True, exist_ok=True)
event = {
    "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "type": "library.sync.completed",
    "source": "23-library-sync.sh",
    "payload": {"indices_rebuilt": True},
    "recipients": ["emperor", "openclaw_main", "dashboard"]
}
(bus_dir / f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z').replace(':', '-').replace('.', '-')}_library.sync.completed.json").write_text(json.dumps(event, indent=2))
print("🧠 Neural bus: library.sync.completed")
PY

echo "✅ Library sync complete"
