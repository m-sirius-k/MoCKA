"""command_index/db.py — command_index.db 管理・スキーマ初期化"""
from __future__ import annotations
import sqlite3
from pathlib import Path

_DEFAULT_DB = Path(__file__).parent.parent / "data" / "command_index.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS commands (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active',
    version     TEXT NOT NULL DEFAULT '1.0.0',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aliases (
    alias       TEXT PRIMARY KEY,
    command_id  TEXT NOT NULL REFERENCES commands(id) ON DELETE CASCADE,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    command_id  TEXT NOT NULL REFERENCES commands(id) ON DELETE CASCADE,
    tag         TEXT NOT NULL,
    PRIMARY KEY (command_id, tag)
);

CREATE TABLE IF NOT EXISTS command_versions (
    command_id  TEXT NOT NULL REFERENCES commands(id) ON DELETE CASCADE,
    version     TEXT NOT NULL,
    changelog   TEXT,
    created_at  TEXT NOT NULL,
    PRIMARY KEY (command_id, version)
);

CREATE TABLE IF NOT EXISTS synonyms (
    word        TEXT NOT NULL,
    synonym     TEXT NOT NULL,
    category    TEXT,
    PRIMARY KEY (word, synonym)
);

CREATE TABLE IF NOT EXISTS usage_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id  TEXT NOT NULL,
    result      TEXT NOT NULL DEFAULT 'success',
    context     TEXT,
    logged_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dependencies (
    from_id     TEXT NOT NULL REFERENCES commands(id),
    to_id       TEXT NOT NULL REFERENCES commands(id),
    dep_type    TEXT NOT NULL DEFAULT 'requires',
    PRIMARY KEY (from_id, to_id)
);

CREATE INDEX IF NOT EXISTS idx_commands_category ON commands(category);
CREATE INDEX IF NOT EXISTS idx_commands_status ON commands(status);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_usage_command ON usage_log(command_id);
"""


class CommandIndexDB:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self._in_memory = str(db_path) == ":memory:" if db_path else False
        if self._in_memory:
            self.path = Path(":memory:")
            self._mem_conn: sqlite3.Connection | None = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
            self._mem_conn.execute("PRAGMA foreign_keys = ON")
            self._mem_conn.executescript(SCHEMA)
        else:
            self.path = Path(db_path) if db_path else _DEFAULT_DB
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._mem_conn = None
            self._init()

    def _init(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        if self._in_memory and self._mem_conn:
            return self._mem_conn
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        conn = self._conn()
        rows = conn.execute(sql, params).fetchall()
        result = [dict(r) for r in rows]
        if not self._in_memory:
            conn.close()
        return result

    def execute_write(self, sql: str, params: tuple = ()) -> int:
        conn = self._conn()
        cur = conn.execute(sql, params)
        conn.commit()
        lastrow = cur.lastrowid or 0
        if not self._in_memory:
            conn.close()
        return lastrow

    def executemany_write(self, sql: str, params_list: list) -> None:
        conn = self._conn()
        conn.executemany(sql, params_list)
        conn.commit()
        if not self._in_memory:
            conn.close()
