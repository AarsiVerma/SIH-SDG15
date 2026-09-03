"""Edge outbox for offline-first sync."""
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from app.core.config import get_settings


class Outbox:
    """SQLite-based outbox for edge mode."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (get_settings().evidence_dir.parent / "edge" / "data" / "outbox.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outbox (
                    id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    synced_at TEXT,
                    attempts INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_synced ON outbox(synced_at)")

    def enqueue(self, kind: str, payload: dict, idempotency_key: Optional[str] = None) -> str:
        key = idempotency_key or str(uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO outbox (id, idempotency_key, kind, payload, created_at, attempts) VALUES (?, ?, ?, ?, ?, 0)",
                (str(uuid4()), key, kind, json.dumps(payload), datetime.utcnow().isoformat()),
            )
        return key

    def get_pending(self, limit: int = 100) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM outbox WHERE synced_at IS NULL ORDER BY created_at LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_synced(self, idempotency_key: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE outbox SET synced_at = ?, attempts = attempts + 1 WHERE idempotency_key = ?",
                (datetime.utcnow().isoformat(), idempotency_key),
            )

    def increment_attempts(self, idempotency_key: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE outbox SET attempts = attempts + 1 WHERE idempotency_key = ?",
                (idempotency_key,),
            )