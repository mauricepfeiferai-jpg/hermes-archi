#!/usr/bin/env python3
"""Query the Mac data index."""
import argparse
import json
import sqlite3
from pathlib import Path

HOME = Path.home()
DB_PATH = HOME / ".mqc" / "mac_data.db"
JSONL_PATH = HOME / ".mqc" / "index.jsonl"


def query_sqlite(label=None, name=None, search=None, recent=None, limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if search:
        c.execute("""
            SELECT m.* FROM mac_data_fts f
            JOIN mac_data m ON m.rowid = f.rowid
            WHERE f.preview MATCH ?
            ORDER BY m.priority ASC, m.mtime_iso DESC
            LIMIT ?
        """, (search, limit))
    elif label:
        c.execute("SELECT * FROM mac_data WHERE label = ? ORDER BY priority ASC, mtime_iso DESC LIMIT ?", (label, limit))
    elif name:
        c.execute("SELECT * FROM mac_data WHERE name LIKE ? ORDER BY mtime_iso DESC LIMIT ?", (f"%{name}%", limit))
    elif recent:
        c.execute("SELECT * FROM mac_data ORDER BY mtime_iso DESC LIMIT ?", (limit,))
    else:
        c.execute("SELECT * FROM mac_data ORDER BY priority ASC, mtime_iso DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--find")
    parser.add_argument("--label")
    parser.add_argument("--search")
    parser.add_argument("--recent", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = query_sqlite(label=args.label, name=args.find, search=args.search, recent=args.recent, limit=args.limit)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    print(f"Found {len(rows)} items")
    for r in rows:
        preview = r.get("preview", "")[:200].replace("\n", " ")
        print(f"\n[{r['label']}] {r['relative']}")
        print(f"  size={r['size']} | modified={r['mtime_iso']}")
        print(f"  preview: {preview}...")


if __name__ == "__main__":
    main()
