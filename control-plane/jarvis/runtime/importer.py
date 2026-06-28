"""Knowledge Importer — feed external data into Jarvis Memory (facts table).

Bridges Maurice's data goldmines into the Core4 brain:
  - Schatzkammer SQLite (6k conversations / 184k messages) — schema-tolerant
  - Markdown / text directories (legal analyses, drafts, obsidian notes)

Imports are stored as `facts` (knowledge), separate from live `conversations`.
Idempotent: each source is tracked in `imported_sources` and skipped on re-run.
FTS5 makes them instantly searchable; embeddings are optional (--embed).

Usage:
    python importer.py --source-db ~/schatzkammer/schatzkammer.db
    python importer.py --source-dir ~/gpe-night/drafts --label legal
    python importer.py --source-db ... --embed       # also compute embeddings
    python importer.py --stats                        # show what's imported
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from memory import MemoryClient  # noqa: E402

# Columns we recognise when auto-detecting a messages table
ROLE_COLS = ("role", "sender", "author", "speaker", "from", "type")
TEXT_COLS = ("content", "text", "message", "body", "msg", "value")
CONV_COLS = ("conversation_id", "conv_id", "chat_id", "thread_id", "session_id")
TIME_COLS = ("ts", "timestamp", "created_at", "date", "time", "created")

MAX_FACT_CHARS = 4000


def _pick(cols: list[str], candidates: tuple[str, ...]) -> str | None:
    low = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in low:
            return low[cand]
    return None


def _detect_message_table(conn: sqlite3.Connection) -> tuple[str, dict] | None:
    """Find the table that looks like chat messages; return (table, colmap)."""
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    best: tuple[int, str, dict] | None = None
    for t in tables:
        if t.startswith("sqlite_") or t == "imported_sources":
            continue
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info('{t}')").fetchall()]
        text_col = _pick(cols, TEXT_COLS)
        if not text_col:
            continue
        colmap = {
            "text": text_col,
            "role": _pick(cols, ROLE_COLS),
            "conv": _pick(cols, CONV_COLS),
            "time": _pick(cols, TIME_COLS),
        }
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM '{t}'").fetchone()[0]
        except sqlite3.Error:
            n = 0
        score = n + (50_000 if colmap["role"] else 0) + (20_000 if colmap["conv"] else 0)
        if best is None or score > best[0]:
            best = (score, t, colmap)
    if best is None:
        return None
    return best[1], best[2]


async def import_db(mem: MemoryClient, db_path: Path, *, embed: bool,
                    label: str, source: str, batch: int = 500) -> int:
    if not db_path.exists():
        print(f"  source DB not found: {db_path}")
        return 0
    src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row
    detected = _detect_message_table(src)
    if not detected:
        print(f"  no message-like table found in {db_path.name}")
        src.close()
        return 0
    table, cm = detected
    print(f"  detected table '{table}' "
          f"(text={cm['text']}, role={cm['role']}, conv={cm['conv']}, time={cm['time']})")

    sel_cols = [cm["text"]]
    for k in ("role", "conv", "time"):
        if cm[k]:
            sel_cols.append(cm[k])
    order = f" ORDER BY {cm['time']}" if cm["time"] else ""
    rows = src.execute(f"SELECT {', '.join(sel_cols)} FROM '{table}'{order}")

    # Preload already-imported keys once — avoids one SELECT per row (184k lookups).
    existing = {r[0] for r in mem.conn.execute("SELECT source_key FROM imported_sources")}

    imported = 0
    pending = 0
    # Batch into explicit transactions instead of autocommit-per-row (~50x faster).
    mem.conn.execute("BEGIN")
    try:
        for r in rows:
            text = (r[cm["text"]] or "").strip()
            if len(text) < 12:
                continue
            role = (r[cm["role"]] if cm["role"] else "") or ""
            conv = str(r[cm["conv"]]) if cm["conv"] else ""

            key = f"{source}:{hashlib.sha1((conv + text[:200]).encode()).hexdigest()[:16]}"
            if key in existing:
                continue
            existing.add(key)

            prefix = f"[{role}] " if role else ""
            fact_text = (prefix + text)[:MAX_FACT_CHARS]
            emb = await mem._embed(fact_text) if embed else None
            mem.write_fact(fact_text, label=label, source=source, embedding=emb)
            mem.mark_source_imported(key, 1)
            imported += 1
            pending += 1
            if pending >= batch:
                mem.conn.execute("COMMIT")
                mem.conn.execute("BEGIN")
                pending = 0
                print(f"    ... {imported} facts imported", end="\r")
        mem.conn.execute("COMMIT")
    except BaseException:
        mem.conn.execute("ROLLBACK")
        raise
    src.close()
    print(f"  imported {imported} facts from {db_path.name}                 ")
    return imported


async def import_dir(mem: MemoryClient, dir_path: Path, *, embed: bool,
                     label: str, source: str,
                     exts=(".md", ".txt")) -> int:
    if not dir_path.exists():
        print(f"  source dir not found: {dir_path}")
        return 0
    files = [p for p in dir_path.rglob("*") if p.suffix.lower() in exts and p.is_file()]
    imported = 0
    for p in files:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if len(content) < 20:
            continue
        key = f"{source}:{p.name}:{hashlib.sha1(content[:500].encode()).hexdigest()[:12]}"
        if mem.is_source_imported(key):
            continue
        fact_text = f"# {p.stem}\n{content}"[:MAX_FACT_CHARS]
        emb = await mem._embed(fact_text) if embed else None
        mem.write_fact(fact_text, label=label, source=f"{source}:{p.name}", embedding=emb)
        mem.mark_source_imported(key, 1)
        imported += 1
    mem.conn.commit()
    print(f"  imported {imported} facts from {dir_path} ({len(files)} files scanned)")
    return imported


def show_stats(mem: MemoryClient) -> None:
    total = mem.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    print(f"Total facts in knowledge base: {total}")
    rows = mem.conn.execute(
        "SELECT COALESCE(label,'(none)') l, COUNT(*) c FROM facts GROUP BY l ORDER BY c DESC"
    ).fetchall()
    for label, c in rows:
        print(f"  {label:24} {c}")
    sources = mem.conn.execute("SELECT COUNT(*) FROM imported_sources").fetchone()[0]
    print(f"Tracked import keys: {sources}")


async def main() -> None:
    ap = argparse.ArgumentParser(description="Import external data into Jarvis Memory")
    ap.add_argument("--source-db", type=Path, help="SQLite DB (e.g. schatzkammer.db)")
    ap.add_argument("--source-dir", type=Path, help="Directory of .md/.txt files")
    ap.add_argument("--label", default="import", help="Category label for facts")
    ap.add_argument("--source", default=None, help="Source tag (default: derived)")
    ap.add_argument("--embed", action="store_true", help="Compute embeddings (slow)")
    ap.add_argument("--stats", action="store_true", help="Show knowledge-base stats")
    args = ap.parse_args()

    mem = MemoryClient()

    if args.stats:
        show_stats(mem)
        return

    if not args.source_db and not args.source_dir:
        ap.error("provide --source-db, --source-dir, or --stats")

    total = 0
    if args.source_db:
        source = args.source or args.source_db.stem
        total += await import_db(mem, args.source_db, embed=args.embed,
                                 label=args.label, source=source)
    if args.source_dir:
        source = args.source or args.source_dir.name
        total += await import_dir(mem, args.source_dir, embed=args.embed,
                                  label=args.label, source=source)

    print(f"\nDone. {total} new facts imported.")
    if not args.embed and total:
        print("Tip: facts are keyword-searchable now (FTS5). "
              "Re-run with --embed for semantic search.")


if __name__ == "__main__":
    asyncio.run(main())
