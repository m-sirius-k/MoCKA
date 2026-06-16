# bridge/mapping_registry.py
# Bridge マッピング永続化レジストリ v1
#
# 責務:
#   BridgeRecord を SQLite に保存・取得・一覧する。
#   意味の書き換えは行わない。状態は必ず保持する。

from __future__ import annotations
import datetime
import sqlite3
from typing import Optional

from bridge.conflict_types import BridgeRecord, ConflictState


DB_DEFAULT = "bridge_registry.db"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class MappingRegistry:
    """
    PHI-OS ↔ Personal Lexicon のデュアルビューを SQLite で永続管理する。

    制約:
      - 意味フィールドを直接上書きする API を持たない
      - 状態（state）は必ず記録される
      - Bridge 以外からの直接変更を想定しない
    """

    def __init__(self, db_path: str = DB_DEFAULT):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS bridge_mappings (
            term             TEXT PRIMARY KEY,
            phi_os_meaning   TEXT,
            personal_meaning TEXT,
            state            TEXT NOT NULL DEFAULT 'NORMAL',
            last_sync        TEXT NOT NULL,
            conflict_reason  TEXT NOT NULL DEFAULT ''
        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_log (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            term             TEXT NOT NULL,
            old_state        TEXT,
            new_state        TEXT NOT NULL,
            reason           TEXT NOT NULL,
            recorded_at      TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ── 保存 ──────────────────────────────────────────────────

    def upsert(self, record: BridgeRecord) -> None:
        """
        BridgeRecord を保存する（新規 or 更新）。
        状態変化があった場合は conflict_log に記録する。
        """
        old = self.get(record.term)
        old_state = old.state.value if old else None

        self.conn.execute(
            """
            INSERT INTO bridge_mappings
                (term, phi_os_meaning, personal_meaning, state, last_sync, conflict_reason)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(term) DO UPDATE SET
                phi_os_meaning   = excluded.phi_os_meaning,
                personal_meaning = excluded.personal_meaning,
                state            = excluded.state,
                last_sync        = excluded.last_sync,
                conflict_reason  = excluded.conflict_reason
            """,
            (
                record.term,
                record.phi_os_meaning,
                record.personal_meaning,
                record.state.value,
                record.last_sync,
                record.conflict_reason,
            ),
        )

        if old_state != record.state.value:
            self.conn.execute(
                """
                INSERT INTO conflict_log (term, old_state, new_state, reason, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.term,
                    old_state,
                    record.state.value,
                    record.conflict_reason,
                    _now(),
                ),
            )

        self.conn.commit()

    # ── 取得 ──────────────────────────────────────────────────

    def get(self, term: str) -> Optional[BridgeRecord]:
        row = self.conn.execute(
            "SELECT * FROM bridge_mappings WHERE term = ?", (term,)
        ).fetchone()
        if row is None:
            return None
        return BridgeRecord.from_dict(dict(row))

    def exists(self, term: str) -> bool:
        return self.get(term) is not None

    # ── 一覧 ──────────────────────────────────────────────────

    def list_all(self) -> list[BridgeRecord]:
        rows = self.conn.execute(
            "SELECT * FROM bridge_mappings ORDER BY term"
        ).fetchall()
        return [BridgeRecord.from_dict(dict(r)) for r in rows]

    def list_by_state(self, state: ConflictState) -> list[BridgeRecord]:
        rows = self.conn.execute(
            "SELECT * FROM bridge_mappings WHERE state = ? ORDER BY term",
            (state.value,),
        ).fetchall()
        return [BridgeRecord.from_dict(dict(r)) for r in rows]

    # ── 衝突ログ参照 ──────────────────────────────────────────

    def conflict_history(self, term: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM conflict_log WHERE term = ? ORDER BY recorded_at",
            (term,),
        ).fetchall()
        return [dict(r) for r in rows]
