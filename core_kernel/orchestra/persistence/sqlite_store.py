"""
MoCKA Core Kernel — orchestra.persistence.sqlite_store

Orchestra実行層のイベント/実行/出力をSQLiteへ永続化するStore。
"""

import dataclasses
import json
import sqlite3

from .schema import SCHEMA

DEFAULT_DB_PATH = "core_kernel/orchestra/data/mocka_orchestra.db"


def _json_default(obj):
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    return str(obj)


def _dumps(value) -> str:
    return json.dumps(value, default=_json_default, ensure_ascii=False)


class SQLiteStore:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        # ":memory:" はsqlite3.connect()ごとに別DBとなるため、
        # その場合のみ単一コネクションを保持して再利用する。
        self._shared_conn = sqlite3.connect(":memory:") if db_path == ":memory:" else None
        self._init_db()

    def _connect(self):
        if self._shared_conn is not None:
            return self._shared_conn
        return sqlite3.connect(self.db_path)

    def _close(self, conn):
        if conn is not self._shared_conn:
            conn.close()

    def _init_db(self):
        if self.db_path != ":memory:":
            import os

            directory = os.path.dirname(self.db_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

        conn = self._connect()
        cur = conn.cursor()
        cur.executescript(SCHEMA)
        conn.commit()
        self._close(conn)

    # -------- event --------
    def save_event(self, event):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            "INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?)",
            (
                event.event_id,
                event.session_id,
                event.event_type,
                event.timestamp,
                _dumps(event.payload),
            ),
        )

        conn.commit()
        self._close(conn)

    # -------- execution --------
    def save_execution(self, execution_id, session_id, node_id, timestamp, context, result):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            "INSERT OR REPLACE INTO executions VALUES (?, ?, ?, ?, ?, ?)",
            (
                execution_id,
                session_id,
                node_id,
                timestamp,
                _dumps(context),
                _dumps(result),
            ),
        )

        conn.commit()
        self._close(conn)

    # -------- output --------
    def save_output(self, output_id, session_id, timestamp, data):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            "INSERT OR REPLACE INTO outputs VALUES (?, ?, ?, ?)",
            (
                output_id,
                session_id,
                timestamp,
                _dumps(data),
            ),
        )

        conn.commit()
        self._close(conn)

    # -------- replay --------
    def load_session_events(self, session_id):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        )
        rows = cur.fetchall()

        self._close(conn)
        return rows
