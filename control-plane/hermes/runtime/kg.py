"""KG-client — minimal wrapper around BlackHole Knowledge Graph (SQLite)."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.models import BusMessage, GoalCard  # noqa: E402

log = logging.getLogger("hermes.kg")

DB_PATH = Path(os.getenv("HERMES_KG_DB", "/var/lib/hermes/knowledge_graph.db"))


SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    props TEXT NOT NULL,
    ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label);

CREATE TABLE IF NOT EXISTS edges (
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    rel TEXT NOT NULL,
    props TEXT,
    ts TEXT NOT NULL,
    PRIMARY KEY (src, dst, rel)
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    type TEXT NOT NULL,
    trace_id TEXT,
    from_agent TEXT,
    to_agent TEXT,
    payload TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_trace ON events(trace_id);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
"""


class KGClient:
    def __init__(self) -> None:
        self.conn: sqlite3.Connection | None = None

    async def connect(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), isolation_level=None, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA busy_timeout=10000")
        self.conn.executescript(SCHEMA)
        log.info("KG ready at %s", DB_PATH)

    async def close(self) -> None:
        if self.conn:
            self.conn.close()

    # ---------- Writes ----------

    async def write_message_event(self, msg: BusMessage) -> None:
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO events (id, ts, type, trace_id, from_agent, to_agent, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (msg.id, msg.ts, f"bus_{msg.type.value}", msg.trace_id or msg.id,
                 msg.from_, msg.to, json.dumps(msg.payload, default=str)[:50_000]),
            )
        except Exception as e:
            log.warning("KG write_message failed: %s", e)

    async def write_goal_event(self, goal: GoalCard, action: str) -> None:
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes (id, label, props, ts) VALUES (?, 'Goal', ?, ?)",
                (goal.id, json.dumps(goal.model_dump(), default=str), goal.created_at),
            )
            self.conn.execute(
                "INSERT OR REPLACE INTO events (id, ts, type, trace_id, from_agent, to_agent, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"evt_{goal.id}_{action}", goal.created_at, f"goal_{action}",
                 goal.id, goal.created_by, goal.owner_agent, json.dumps({"title": goal.title, "status": goal.status.value})),
            )
        except Exception as e:
            log.warning("KG write_goal failed: %s", e)

    async def write_node(self, label: str, node_id: str, props: dict, ts: str) -> None:
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes (id, label, props, ts) VALUES (?, ?, ?, ?)",
                (node_id, label, json.dumps(props, default=str), ts),
            )
        except Exception as e:
            log.warning("KG write_node failed: %s", e)

    async def write_edge(self, src: str, dst: str, rel: str, props: dict | None, ts: str) -> None:
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO edges (src, dst, rel, props, ts) VALUES (?, ?, ?, ?, ?)",
                (src, dst, rel, json.dumps(props) if props else None, ts),
            )
        except Exception as e:
            log.warning("KG write_edge failed: %s", e)

    # ---------- Reads ----------

    async def get_trace(self, trace_id: str) -> dict[str, Any]:
        if not self.conn:
            return {"trace_id": trace_id, "events": []}
        cur = self.conn.execute(
            "SELECT id, ts, type, from_agent, to_agent, payload FROM events WHERE trace_id = ? ORDER BY ts",
            (trace_id,),
        )
        rows = cur.fetchall()
        events = [
            {"id": r[0], "ts": r[1], "type": r[2], "from": r[3], "to": r[4],
             "payload": json.loads(r[5]) if r[5] else None}
            for r in rows
        ]
        return {"trace_id": trace_id, "events": events}

    async def find_nodes(self, label: str, limit: int = 100) -> list[dict]:
        cur = self.conn.execute(
            "SELECT id, label, props, ts FROM nodes WHERE label = ? ORDER BY ts DESC LIMIT ?",
            (label, limit),
        )
        return [{"id": r[0], "label": r[1], "props": json.loads(r[2]), "ts": r[3]} for r in cur.fetchall()]
