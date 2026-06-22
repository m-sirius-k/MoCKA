# relay/replay_audit.py
# Relay Phase4.5 - Replay監査層(最小実装)。
#
# 目的: Replayが「実行・比較・記録」できることを保証する境界部品。
# スコープは最小限: Drift検知 + Audit Log記録のみ。これ以上の機能(自動修復・
# alertルーティング等)は持たない。
#
# 絶対条件:
#   - kernel/snapshot/queue/event構造には触れない
#   - hybrid replayの戻り値はv1側のまま(return_v1原則)、本モジュールは記録のみ行う

import hashlib
import json
import sqlite3
import time
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "relay" / "event_log.db"


def compute_state_hash(state: dict) -> str:
    payload = json.dumps(state, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ReplayAuditLog:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS replay_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    replay_mode TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    state_hash TEXT NOT NULL,
                    match INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def record(self, replay_mode: str, event_hash: str, state_hash: str, match: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO replay_audit_log
                    (replay_mode, event_hash, state_hash, match, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (replay_mode, event_hash, state_hash, int(match), int(time.time())),
            )
            conn.commit()

    def get_recent(self, limit: int = 10) -> list:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT id, replay_mode, event_hash, state_hash, match, timestamp "
                "FROM replay_audit_log ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return [
                {
                    "id": row[0],
                    "replay_mode": row[1],
                    "event_hash": row[2],
                    "state_hash": row[3],
                    "match": bool(row[4]),
                    "timestamp": row[5],
                }
                for row in cursor.fetchall()
            ]
