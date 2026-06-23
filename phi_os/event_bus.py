# phi_os/event_bus.py
# Pure append-only event bus（GL7 -> PHI-OS の唯一の接続経路）
#
# 設計原則(Phase2確定): GL7はPHI-OSの関数を呼び出さない・state参照しない・
# 同期待ちしない。GL7はここにeventをappendするだけ。PHI-OS側は別途
# このバスを読み取って(consume)処理する。GL7とPHI-OSは時間的に非同期。
import sqlite3
import time
import secrets
import json
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_bus (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            payload TEXT,
            consumed INTEGER DEFAULT 0
        )
    ''')


def _next_event_id() -> str:
    d = datetime.now(timezone.utc).strftime('%Y%m%d')
    micros_of_day = time.time_ns() // 1000 % 1_000_000_000
    return f'EB{d}_{micros_of_day:09d}{secrets.token_hex(2)}'


def append(event_type: str, payload: dict, conn=None) -> dict:
    """中立なバスへeventをappendするだけ。呼び出し元(GL7)は結果を待たない・参照しない。"""
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        event = {
            "event_id": _next_event_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "payload": json.dumps(payload, ensure_ascii=False, sort_keys=True),
            "consumed": 0,
        }
        conn.execute(
            'INSERT INTO event_bus (event_id, timestamp, type, payload, consumed) VALUES (?, ?, ?, ?, ?)',
            (event["event_id"], event["timestamp"], event["type"], event["payload"], event["consumed"]),
        )
        conn.commit()
        return event
    finally:
        if owns_conn:
            conn.close()


def read_unconsumed(event_type: str | None = None, conn=None) -> list:
    """PHI-OS側がpoll方式で読み取るための関数。GL7側からは呼ばれない。"""
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        if event_type:
            rows = conn.execute(
                'SELECT * FROM event_bus WHERE consumed = 0 AND type = ? ORDER BY timestamp ASC',
                (event_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT * FROM event_bus WHERE consumed = 0 ORDER BY timestamp ASC'
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if owns_conn:
            conn.close()


def mark_consumed(event_id: str, conn=None) -> None:
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        conn.execute('UPDATE event_bus SET consumed = 1 WHERE event_id = ?', (event_id,))
        conn.commit()
    finally:
        if owns_conn:
            conn.close()
