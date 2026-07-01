#!/usr/bin/env python3
"""Index personal data on Maurice's Mac for Hermes/OpenClaw access."""
import json
import sqlite3
import os
import subprocess
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MQC_DIR = HOME / ".mqc"
MQC_DIR.mkdir(exist_ok=True)
JSONL_PATH = MQC_DIR / "index.jsonl"
DB_PATH = MQC_DIR / "mac_data.db"

INDEX_ROOTS = [
    (HOME / "ai-empire", "ai-empire", 1),
    (HOME / ".hermes", "hermes-config", 2),
    (HOME / ".openclaw" / "workspace" / "ai-empire", "openclaw-workspace", 2),
    (HOME / ".codex", "codex-state", 2),
]

OPTIONAL_ROOTS = [
    (HOME / "Documents" / "Recht", "legal-documents", 3),
    (HOME / "Documents" / "BMA", "bma-documents", 3),
    (HOME / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents", "obsidian", 2),
]

EXCLUDED = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "cache", "logs", "tmp", "temp", "archive", "backups",
    ".DS_Store", ".pytest_cache", ".mypy_cache", "dist", "build",
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js",
    ".html", ".css", ".toml", ".cfg", ".ini", ".log", ".csv",
}

MAX_PREVIEW = 2000
MAX_FILE_SIZE = 1024 * 1024


def should_index(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED:
        return False
    if path.stat().st_size > MAX_FILE_SIZE:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name in {"config.yaml", "openclaw.json", "auth.json", "memory.db"}:
        return True
    return False


def read_preview(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(MAX_PREVIEW)
    except Exception:
        return ""


def index_files():
    entries = []
    for root, label, priority in INDEX_ROOTS + OPTIONAL_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if not should_index(path):
                continue
            stat = path.stat()
            entries.append({
                "path": str(path),
                "relative": str(path.relative_to(HOME)),
                "label": label,
                "priority": priority,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "mtime_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "ext": path.suffix.lower(),
                "name": path.name,
                "preview": read_preview(path),
            })
    return entries


def index_system():
    entries = []
    try:
        crontab = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)
        if crontab.returncode == 0:
            entries.append({
                "path": "crontab://current", "relative": "system/crontab", "label": "system", "priority": 1,
                "size": len(crontab.stdout), "mtime": datetime.now().timestamp(),
                "mtime_iso": datetime.now().isoformat(), "ext": "", "name": "crontab",
                "preview": crontab.stdout[:MAX_PREVIEW],
            })
    except Exception:
        pass
    try:
        df = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        entries.append({
            "path": "system://disk-usage", "relative": "system/disk-usage", "label": "system", "priority": 1,
            "size": len(df.stdout), "mtime": datetime.now().timestamp(),
            "mtime_iso": datetime.now().isoformat(), "ext": "", "name": "disk-usage", "preview": df.stdout,
        })
    except Exception:
        pass
    try:
        ps = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        procs = "\n".join([line for line in ps.stdout.splitlines() if any(x in line for x in ["hermes", "openclaw", "ollama", "codex", "claude"])])
        entries.append({
            "path": "system://agent-processes", "relative": "system/agent-processes", "label": "system", "priority": 1,
            "size": len(procs), "mtime": datetime.now().timestamp(),
            "mtime_iso": datetime.now().isoformat(), "ext": "", "name": "agent-processes", "preview": procs[:MAX_PREVIEW],
        })
    except Exception:
        pass
    return entries


def write_jsonl(entries):
    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def write_sqlite(entries):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS mac_data")
    c.execute("""
        CREATE TABLE mac_data (
            path TEXT PRIMARY KEY, relative TEXT, label TEXT, priority INTEGER,
            size INTEGER, mtime_iso TEXT, ext TEXT, name TEXT, preview TEXT
        )
    """)
    c.execute("CREATE INDEX idx_label ON mac_data(label)")
    c.execute("CREATE INDEX idx_name ON mac_data(name)")
    c.execute("DROP TABLE IF EXISTS mac_data_fts")
    c.execute("CREATE VIRTUAL TABLE mac_data_fts USING fts5(preview, content='mac_data', content_rowid='rowid')")
    for e in entries:
        c.execute("INSERT OR REPLACE INTO mac_data VALUES (?,?,?,?,?,?,?,?,?)",
                  (e["path"], e["relative"], e["label"], e["priority"], e["size"], e["mtime_iso"], e["ext"], e["name"], e["preview"]))
    c.execute("INSERT INTO mac_data_fts(rowid, preview) SELECT rowid, preview FROM mac_data")
    conn.commit()
    conn.close()


def main():
    print(f"[{datetime.now().isoformat()}] Starting Mac data index...")
    entries = index_files() + index_system()
    write_jsonl(entries)
    write_sqlite(entries)
    print(f"Indexed {len(entries)} items")
    print(f"JSONL: {JSONL_PATH}")
    print(f"SQLite: {DB_PATH}")


if __name__ == "__main__":
    main()
