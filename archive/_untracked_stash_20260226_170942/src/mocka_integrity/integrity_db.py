"""
Integrity DB access and schema
date: 2026-02-24

note:
- This DB is separate from governance DB.
- It stores anchors and attestation logs.
- Use explicit migrations only.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple


DEFAULT_INTEGRITY_DB_PATH = os.path.join("infield", "phase16", "db", "integrity.db")


SCHEMA_SQL = r"""
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS proof_anchor (
  anchor_id TEXT PRIMARY KEY,
  created_utc TEXT NOT NULL,
  source_event_id TEXT NOT NULL,
  source_chain_hash TEXT NOT NULL,
  final_chain_hash TEXT NOT NULL,
  signature_ed25519 TEXT NOT NULL,
  public_key_id TEXT NOT NULL,
  note TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_proof_anchor_final_chain_hash
  ON proof_anchor(final_chain_hash);

CREATE INDEX IF NOT EXISTS idx_proof_anchor_source_event_id
  ON proof_anchor(source_event_id);

CREATE TABLE IF NOT EXISTS attestation_log (
  attestation_id TEXT PRIMARY KEY,
  created_utc TEXT NOT NULL,
  anchor_id TEXT NOT NULL,
  verifier TEXT NOT NULL,
  result TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES proof_anchor(anchor_id)
);

CREATE INDEX IF NOT EXISTS idx_attestation_log_anchor_id
  ON attestation_log(anchor_id);
"""


@dataclass(frozen=True)
class IntegrityDBConfig:
    db_path: str = DEFAULT_INTEGRITY_DB_PATH


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def connect_rw(cfg: IntegrityDBConfig) -> sqlite3.Connection:
    _ensure_parent_dir(cfg.db_path)
    conn = sqlite3.connect(cfg.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def connect_ro(cfg: IntegrityDBConfig) -> sqlite3.Connection:
    # SQLite read-only URI
    uri = f"file:{cfg.db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def migrate_schema(cfg: IntegrityDBConfig) -> Tuple[bool, str]:
    """
    Apply schema. Returns (ok, message).
    """
    try:
        conn = connect_rw(cfg)
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()
        return True, f"OK: schema applied db={cfg.db_path}"
    except Exception as e:
        return False, f"NG: migrate failed: {e}"


def table_exists_ro(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    )
    return cur.fetchone() is not None
