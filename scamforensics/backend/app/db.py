import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.getenv("SCAMFORENSICS_DB", Path(__file__).resolve().parents[1] / "scamforensics.db"))


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS evidence (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              case_id TEXT NOT NULL DEFAULT 'CASE-DEMO',
              filename TEXT NOT NULL,
              kind TEXT NOT NULL,
              raw_text TEXT NOT NULL,
              timestamp TEXT,
              ts_source TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS entities (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              evidence_id INTEGER NOT NULL,
              type TEXT NOT NULL,
              value TEXT NOT NULL,
              FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_entities_value ON entities(type, value);
            """
        )


def rows(sql, params=()):
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def row(sql, params=()):
    with connect() as conn:
        result = conn.execute(sql, params).fetchone()
        return dict(result) if result else None
