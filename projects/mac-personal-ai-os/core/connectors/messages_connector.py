#!/usr/bin/env python3
"""Read-only connector for Apple Messages via chat.db.

Never writes. Returns recent message previews per chat, no full content unless needed.
"""
import argparse
import json
import sqlite3
from pathlib import Path

CHAT_DB = Path.home() / "Library/Messages/chat.db"

# Apple stores dates as nanoseconds since Cocoa epoch (2001-01-01)
COCOA_OFFSET = 978307200


def read_messages(limit: int = 10) -> dict:
    if not CHAT_DB.exists():
        return {"success": False, "source": "messages", "backend": "sqlite", "error": f"DB not found: {CHAT_DB}"}
    try:
        conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        # Recent messages with handle/phone/email, grouped by chat, limited
        cur = conn.execute(
            """
            SELECT m.ROWID AS id,
                   m.text,
                   m.is_from_me,
                   m.date / 1000000000 + ? AS date_unix,
                   h.id AS handle,
                   c.display_name AS chat_name
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            LEFT JOIN chat c ON c.ROWID = cmj.chat_id
            WHERE m.is_from_me = 0
              AND m.text IS NOT NULL
              AND m.text != ''
            ORDER BY m.date DESC
            LIMIT ?
            """,
            (COCOA_OFFSET, limit),
        )
        rows = [dict(row) for row in cur.fetchall()]
        messages = []
        for r in rows:
            text = r.get("text") or ""
            if len(text) > 120:
                text = text[:120] + "…"
            messages.append({
                "chat": r.get("chat_name") or r.get("handle") or "Unknown",
                "handle": r.get("handle") or "me",
                "from_me": bool(r.get("is_from_me")),
                "date": r.get("date_unix"),
                "preview": text,
            })
        return {"success": True, "source": "messages", "backend": "sqlite", "count": len(messages), "messages": messages}
    except Exception as e:
        return {"success": False, "source": "messages", "backend": "sqlite", "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC Apple Messages SQLite read-only connector")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = read_messages(limit=args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Messages: {result.get('count')} recent")
        for m in result.get("messages", [])[:args.limit]:
            print(f"- [{m.get('date', '?')}] {m.get('handle', '?')}: {m.get('preview', '')}")


if __name__ == "__main__":
    main()
