"""Jarvis Memory — recall + write for conversations.

MVP: SQLite-backed conversation log. Vector-recall via Ollama embeddings.
Future (Phase 3): wire CORE Engine + Galaxia Vector DB.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.ollama import OllamaClient  # noqa: E402

log = logging.getLogger("jarvis.memory")

DB_PATH = Path(os.getenv("JARVIS_MEMORY_DB", "/var/lib/jarvis/memory.db"))
EMBED_MODEL = os.getenv("JARVIS_EMBED_MODEL", "nomic-embed-text")
CONTEXT_TOKEN_BUDGET = 2000


SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    user_id TEXT NOT NULL,
    user_text TEXT NOT NULL,
    jarvis_reply TEXT NOT NULL,
    intent TEXT,
    embedding TEXT
);
CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id, ts DESC);

CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    user_id TEXT NOT NULL,
    label TEXT,
    source TEXT,
    text TEXT NOT NULL,
    embedding TEXT
);
CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source);

CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    text,
    label,
    source,
    content='facts',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, text, label, source)
    VALUES (new.id, new.text, new.label, new.source);
END;

CREATE TABLE IF NOT EXISTS imported_sources (
    source_key TEXT PRIMARY KEY,
    imported_at TEXT,
    count INTEGER
);
"""


class MemoryClient:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), isolation_level=None, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._migrate()
        self.conn.executescript(SCHEMA)
        self.ollama = OllamaClient()

    def _migrate(self) -> None:
        """Add columns introduced after first release to pre-existing DBs."""
        cur = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='facts'"
        )
        if cur.fetchone():
            cols = {r[1] for r in self.conn.execute("PRAGMA table_info(facts)").fetchall()}
            if "source" not in cols:
                self.conn.execute("ALTER TABLE facts ADD COLUMN source TEXT")

    async def write_turn(self, user_id: str, user_text: str, jarvis_reply: str, intent: str | None) -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        emb = await self._embed(user_text)
        try:
            self.conn.execute(
                "INSERT INTO conversations (ts, user_id, user_text, jarvis_reply, intent, embedding) VALUES (?, ?, ?, ?, ?, ?)",
                (ts, user_id, user_text, jarvis_reply, intent, json.dumps(emb) if emb else None),
            )
        except Exception as e:
            log.warning("memory write failed: %s", e)

    async def recall(self, query: str, user_id: str = "maurice") -> str:
        """Return assembled context string under CONTEXT_TOKEN_BUDGET."""
        parts: list[str] = []
        # 1) last 5 turns (verbatim)
        cur = self.conn.execute(
            "SELECT ts, user_text, jarvis_reply FROM conversations WHERE user_id = ? ORDER BY ts DESC LIMIT 5",
            (user_id,),
        )
        recent = cur.fetchall()
        if recent:
            parts.append("## Letzte Turns")
            for ts, u, j in reversed(recent):
                parts.append(f"[{ts}] Maurice: {u[:200]}\n[{ts}] Jarvis: {j[:200]}")
        # 2) semantic hits from live conversations
        hits = await self.search(query, limit=3)
        if hits:
            parts.append("## Semantisch ähnlich")
            for h in hits:
                parts.append(f"- {h['user_text'][:200]} → {h['jarvis_reply'][:200]}")
        # 3) knowledge-base hits (imported facts: schatzkammer, legal, etc.)
        kb = self.search_facts(query, limit=4)
        if kb:
            parts.append("## Aus dem Wissensspeicher")
            for f in kb:
                src = f.get("source") or f.get("label") or "fact"
                parts.append(f"- [{src}] {f['text'][:240]}")
        return "\n\n".join(parts)[:CONTEXT_TOKEN_BUDGET * 4]  # rough char limit

    def write_fact(self, text: str, *, label: str | None = None,
                   source: str | None = None, user_id: str = "maurice",
                   embedding: list[float] | None = None) -> None:
        """Store a single knowledge fact (synchronous; used by importers)."""
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.conn.execute(
            "INSERT INTO facts (ts, user_id, label, source, text, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, user_id, label, source, text, json.dumps(embedding) if embedding else None),
        )

    def search_facts(self, query: str, limit: int = 5) -> list[dict]:
        """Fast FTS5 keyword search over the knowledge base (no embeddings needed)."""
        match = _fts_query(query)
        if not match:
            return []
        try:
            cur = self.conn.execute(
                "SELECT f.text, f.label, f.source, f.ts "
                "FROM facts_fts JOIN facts f ON f.id = facts_fts.rowid "
                "WHERE facts_fts MATCH ? ORDER BY rank LIMIT ?",
                (match, limit),
            )
            return [{"text": r[0], "label": r[1], "source": r[2], "ts": r[3]}
                    for r in cur.fetchall()]
        except sqlite3.OperationalError as e:
            log.debug("fts search failed: %s", e)
            return []

    def is_source_imported(self, source_key: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM imported_sources WHERE source_key = ?", (source_key,)
        )
        return cur.fetchone() is not None

    def mark_source_imported(self, source_key: str, count: int) -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.conn.execute(
            "INSERT OR REPLACE INTO imported_sources (source_key, imported_at, count) VALUES (?, ?, ?)",
            (source_key, ts, count),
        )

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        emb = await self._embed(query)
        if not emb:
            # fallback: latest turns
            cur = self.conn.execute(
                "SELECT user_text, jarvis_reply, ts FROM conversations ORDER BY ts DESC LIMIT ?",
                (limit,),
            )
            return [{"user_text": r[0], "jarvis_reply": r[1], "ts": r[2], "score": 0.0}
                    for r in cur.fetchall()]
        cur = self.conn.execute(
            "SELECT user_text, jarvis_reply, ts, embedding FROM conversations WHERE embedding IS NOT NULL ORDER BY ts DESC LIMIT 500"
        )
        scored: list[tuple[float, dict]] = []
        for row in cur.fetchall():
            try:
                other = json.loads(row[3])
            except (json.JSONDecodeError, TypeError):
                continue
            s = _cosine(emb, other)
            scored.append((s, {"user_text": row[0], "jarvis_reply": row[1], "ts": row[2], "score": s}))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [d for _, d in scored[:limit]]

    async def _embed(self, text: str) -> list[float] | None:
        try:
            return await self.ollama.embed(EMBED_MODEL, text)
        except Exception as e:
            log.debug("embedding failed (ollama unreachable?): %s", e)
            return None


def _fts_query(query: str) -> str:
    """Turn free text into a safe FTS5 OR-query of word tokens."""
    import re
    tokens = re.findall(r"\w{3,}", query.lower())
    if not tokens:
        return ""
    return " OR ".join(f'"{t}"' for t in tokens[:12])


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if (na and nb) else 0.0
