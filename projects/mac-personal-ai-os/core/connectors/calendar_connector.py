#!/usr/bin/env python3
"""Read-only connector for Apple Calendar via direct Calendar.sqlitedb.

Only reads; never writes. Uses EventKit CoreData schema (macOS).
"""
import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

CALENDAR_DB = Path.home() / "Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb"


def read_calendar(days: int = 30, limit: int = 20) -> dict:
    if not CALENDAR_DB.exists():
        return {"success": False, "source": "calendar", "backend": "sqlite", "error": f"DB not found: {CALENDAR_DB}"}
    now_epoch = datetime.now().timestamp()
    end_epoch = now_epoch + days * 24 * 3600
    # start_date/end_date are stored as seconds since Cocoa epoch (2001-01-01)
    cocoa_offset = 978307200
    now_cocoa = now_epoch - cocoa_offset
    end_cocoa = end_epoch - cocoa_offset
    try:
        conn = sqlite3.connect(f"file:{CALENDAR_DB}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """
            SELECT c.title AS calendar, i.summary AS title,
                   datetime(i.start_date + 978307200, 'unixepoch') AS start,
                   datetime(i.end_date + 978307200, 'unixepoch') AS end,
                   i.all_day
            FROM CalendarItem i
            JOIN Calendar c ON c.ROWID = i.calendar_id
            WHERE i.start_date >= ? AND i.start_date <= ?
            ORDER BY i.start_date
            LIMIT ?
            """,
            (now_cocoa, end_cocoa, limit),
        )
        events = [dict(row) for row in cur.fetchall()]
        return {"success": True, "source": "calendar", "backend": "sqlite", "window_days": days, "count": len(events), "events": events}
    except Exception as e:
        return {"success": False, "source": "calendar", "backend": "sqlite", "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC Apple Calendar SQLite read-only connector")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = read_calendar(days=args.days, limit=args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Calendar: {result.get('count')} events")
        for e in result.get("events", [])[:20]:
            print(f"- [{e.get('start', '?')}] {e.get('title', '?')}")


if __name__ == "__main__":
    main()
