"""Small SQLite event store used for durable audit history."""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class EventStore:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialise()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _initialise(self):
        with self._lock, self._connection() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    value_json TEXT,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    scenario TEXT NOT NULL,
                    is_attack INTEGER NOT NULL DEFAULT 0,
                    detected INTEGER NOT NULL DEFAULT 0,
                    transport TEXT NOT NULL DEFAULT 'SIMULATED'
                )"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
            conn.commit()

    def add_event(self, event: dict[str, Any]):
        with self._lock, self._connection() as conn:
            conn.execute(
                """INSERT INTO events (
                    timestamp, request_id, source_id, target_id, action, value_json,
                    status, severity, event_type, reason, scenario, is_attack,
                    detected, transport
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event["timestamp"], event["request_id"], event["source_id"],
                    event["target_id"], event["action"], json.dumps(event.get("value")),
                    event["status"], event["severity"], event["event_type"],
                    event["reason"], event.get("scenario", "manual"),
                    int(bool(event.get("is_attack"))), int(bool(event.get("detected"))),
                    event.get("transport", "SIMULATED"),
                ),
            )
            conn.commit()

    def list_events(self, limit: int = 500, status: str | None = None):
        query = "SELECT * FROM events"
        args: list[Any] = []
        if status and status != "All":
            query += " WHERE status = ?"
            args.append(status.upper())
        query += " ORDER BY id DESC LIMIT ?"
        args.append(max(1, min(int(limit), 10000)))
        with self._connection() as conn:
            rows = conn.execute(query, args).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["value"] = json.loads(item.pop("value_json") or "null")
            item["is_attack"] = bool(item["is_attack"])
            item["detected"] = bool(item["detected"])
            result.append(item)
        return result

    def count_events(self):
        with self._connection() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])

    def clear(self):
        with self._lock, self._connection() as conn:
            conn.execute("DELETE FROM events")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='events'")
            conn.commit()

    def metrics(self):
        with self._connection() as conn:
            row = conn.execute(
                """SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status='ALLOWED' THEN 1 ELSE 0 END) AS allowed,
                    SUM(CASE WHEN status='BLOCKED' THEN 1 ELSE 0 END) AS blocked,
                    SUM(CASE WHEN is_attack=1 THEN 1 ELSE 0 END) AS attack_attempts,
                    SUM(CASE WHEN is_attack=1 AND detected=1 THEN 1 ELSE 0 END) AS detected_attacks,
                    SUM(CASE WHEN severity IN ('HIGH','CRITICAL') THEN 1 ELSE 0 END) AS high_alerts
                FROM events"""
            ).fetchone()
        return {key: int(row[key] or 0) for key in row.keys()}
