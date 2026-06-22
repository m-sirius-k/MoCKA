# phi_os/event_replay.py
# Event Audit / Replay Layer — READ ONLY extension of Event Integrity Framework v1.0
#
# このモジュールは新たな真実層・新たな書き込み経路を作らない。
# 唯一の真実層は phi_os.event_gate.process_event() / data/mocka_events.db のままであり、
# 本モジュールはそれを「読むだけ」で状態再構築（replay）と既存integrity検証の
# 一体公開を行う。DB書き込み・process_event呼び出し・event_gate迂回は一切行わない。

import sqlite3
from pathlib import Path

from . import integrity

_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')

# replayで状態に取り込む5W1Hカラム（events表に実在する列のみ）
_STATE_COLUMNS = [
    "event_id", "when_ts", "who_actor", "where_component", "where_path",
    "why_purpose", "how_trigger", "title", "short_summary",
    "before_state", "after_state", "change_type", "impact_scope", "impact_result",
]


def _get_conn(db_path: str = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class EventReplayer:
    """events表をwhat_type別に集約し、状態を再構築する読み取り専用クラス。"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH

    def replay(self, start_seq: int = None, end_seq: int = None) -> dict:
        conn = _get_conn(self.db_path)
        try:
            where = []
            params = []
            if start_seq is not None or end_seq is not None:
                # events表自体にseqは無いため、event_signatures経由でseq範囲をevent_idに変換
                sig_where = []
                if start_seq is not None:
                    sig_where.append("seq >= ?")
                    params.append(start_seq)
                if end_seq is not None:
                    sig_where.append("seq <= ?")
                    params.append(end_seq)
                sig_sql = "WHERE " + " AND ".join(sig_where)
                ids = [r["event_id"] for r in conn.execute(
                    f"SELECT event_id FROM event_signatures {sig_sql}", params
                ).fetchall()]
                if not ids:
                    return {}
                placeholders = ",".join("?" for _ in ids)
                where.append(f"event_id IN ({placeholders})")
                params = ids

            where_sql = ("WHERE " + " AND ".join(where)) if where else ""
            rows = conn.execute(
                f"SELECT * FROM events {where_sql} ORDER BY when_ts ASC", params
            ).fetchall()

            state = {}
            for row in rows:
                r = dict(row)
                key = r.get("what_type") or "_untyped"
                state.setdefault(key, []).append(
                    {col: r.get(col) for col in _STATE_COLUMNS}
                )
            return state
        finally:
            conn.close()


class EventAuditEngine:
    """既存Event Integrity Framework(integrity.verify_chain/diagnose)とReplayを一体公開する。"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._replayer = EventReplayer(self.db_path)

    def replay(self, start_seq: int = None, end_seq: int = None) -> dict:
        return self._replayer.replay(start_seq, end_seq)

    def verify(self, start_seq: int = None, end_seq: int = None) -> dict:
        conn = _get_conn(self.db_path)
        try:
            return integrity.verify_chain(conn, start_seq, end_seq)
        finally:
            conn.close()

    def diagnose(self, start_seq: int = None, end_seq: int = None) -> list:
        result = self.verify(start_seq, end_seq)
        return integrity.diagnose(result["anomalies"])
