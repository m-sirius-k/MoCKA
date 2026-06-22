# relay/repositories_sqlite.py
# Relay Phase5 Step2 - Layer B(実装自由層)。relay/repositories.pyで固定した
# Layer A契約(EventRepository等)のSQLite実装を提供する。
#
# 段階実装ルール(確定): Event -> Snapshot -> Queue の順で単独完成・確認してから次に進む。
# SnapshotはEvent前提、QueueはState前提のため、依存元のEventRepositoryを最優先で実装する。
#
# 本ファイルはStep2-1として LocalEventRepository のみを実装する。
# Snapshot/Queueの実装はStep2-2/2-3で追加する。

import json
import sqlite3
import time
from pathlib import Path

import uuid

from .repositories import EventRepository, SnapshotRepository, QueueRepository

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "relay" / "event_log.db"


class LocalEventRepository(EventRepository):
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
                CREATE TABLE IF NOT EXISTS event_log (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    payload JSON NOT NULL
                )
                """
            )
            conn.commit()

    def append_event(self, event: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO event_log (timestamp, payload) VALUES (?, ?)",
                (int(time.time()), json.dumps(event, ensure_ascii=False)),
            )
            conn.commit()

    def get_events(self, from_id: str = None) -> list:
        with self._connect() as conn:
            if from_id is None:
                cursor = conn.execute(
                    "SELECT event_id, timestamp, payload FROM event_log ORDER BY event_id"
                )
            else:
                cursor = conn.execute(
                    "SELECT event_id, timestamp, payload FROM event_log WHERE event_id > ? ORDER BY event_id",
                    (int(from_id),),
                )
            return [
                {
                    "event_id": row[0],
                    "timestamp": row[1],
                    "event": json.loads(row[2]),
                }
                for row in cursor.fetchall()
            ]


class LocalSnapshotRepository(SnapshotRepository):
    # Step2-2: 最小完成スコープ(save_snapshot/load_latestのみ)。
    # Snapshotは時間の圧縮点であり、Eventを改変せずQueueにも依存しない。
    # Replay Engine本体との接続は別ステップで行う。

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
                CREATE TABLE IF NOT EXISTS snapshot (
                    snapshot_id TEXT PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    state JSON NOT NULL,
                    last_event_id TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_snapshot(self, snapshot: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO snapshot (snapshot_id, node_id, timestamp, state, last_event_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    snapshot["snapshot_id"],
                    snapshot["node_id"],
                    int(snapshot.get("timestamp", time.time())),
                    json.dumps(snapshot["state"], ensure_ascii=False),
                    str(snapshot["last_event_id"]),
                ),
            )
            conn.commit()

    def load_latest(self) -> dict:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT snapshot_id, node_id, timestamp, state, last_event_id "
                "FROM snapshot ORDER BY timestamp DESC, snapshot_id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "snapshot_id": row[0],
                "node_id": row[1],
                "timestamp": row[2],
                "state": json.loads(row[3]),
                "last_event_id": row[4],
            }


class LocalQueueRepository(QueueRepository):
    # Step2-3: 未確定状態の制御層。push/pop/update_statusの3操作のみに限定。
    # 状態遷移: pending -> processing -> done / failed
    # EventRepository/SnapshotRepository/ReplayEngineには結合しない。

    def __init__(self, db_path: Path = DEFAULT_DB_PATH, node_id: str = "local"):
        self.db_path = Path(db_path)
        self.node_id = node_id
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_queue (
                    queue_id TEXT PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    payload JSON NOT NULL,
                    status TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def push(self, event: dict) -> None:
        now = int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO event_queue
                    (queue_id, node_id, event_id, payload, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    self.node_id,
                    str(event.get("event_id", uuid.uuid4())),
                    json.dumps(event, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            conn.commit()

    def pop(self) -> dict:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT queue_id, node_id, event_id, payload, status, created_at, updated_at "
                "FROM event_queue WHERE status = 'pending' ORDER BY created_at LIMIT 1"
            )
            row = cursor.fetchone()
            if row is None:
                return None

            now = int(time.time())
            conn.execute(
                "UPDATE event_queue SET status = 'processing', updated_at = ? WHERE queue_id = ?",
                (now, row[0]),
            )
            conn.commit()

            return {
                "queue_id": row[0],
                "node_id": row[1],
                "event_id": row[2],
                "event": json.loads(row[3]),
                "status": "processing",
                "created_at": row[5],
                "updated_at": now,
            }

    def update_status(self, queue_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE event_queue SET status = ?, updated_at = ? WHERE queue_id = ?",
                (status, int(time.time()), queue_id),
            )
            conn.commit()
