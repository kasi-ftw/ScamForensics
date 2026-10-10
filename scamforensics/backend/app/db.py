import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .high_risk_domains import CYBERTRACE_2026_HIGH_RISK_DOMAINS

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
              file_path TEXT,
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
            CREATE TABLE IF NOT EXISTS high_risk_domains (
              domain TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.executemany(
            "INSERT OR IGNORE INTO high_risk_domains(domain, source) VALUES (?, ?)",
            [(domain, "Cybertrace 2026 list (user-provided)") for domain in CYBERTRACE_2026_HIGH_RISK_DOMAINS],
        )
        evidence_columns = {item[1] for item in conn.execute("PRAGMA table_info(evidence)")}
        if "file_path" not in evidence_columns:
            conn.execute("ALTER TABLE evidence ADD COLUMN file_path TEXT")


def rows(sql, params=()):
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def row(sql, params=()):
    with connect() as conn:
        result = conn.execute(sql, params).fetchone()
        return dict(result) if result else None


def high_risk_domain_matches(text: str) -> list[str]:
    """Return blocklist domains found as complete host names in uploaded evidence."""
    with connect() as conn:
        domains = [item[0] for item in conn.execute("SELECT domain FROM high_risk_domains")]
    lowered = text.lower()
    return [domain for domain in domains if re.search(rf"(?<![a-z0-9.-])(?:www\\.)?{re.escape(domain)}(?![a-z0-9.-])", lowered)]
