"""
vasAI Core: Evidence Ledger — 「なぜ起きたか」を記録するDB。
event_store が「何が起きたか」なら、Evidence Ledger は「なぜ起きたか」。
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_DB = Path(__file__).parent.parent / "data" / "vasai_evidence.db"
_lock = threading.Lock()
_conn_cache: dict[str, sqlite3.Connection] = {}

EVIDENCE_TYPES = ("FACT", "ASSUMPTION", "CONSTRAINT", "INTENT")


def _ev_db_path() -> Path:
    import os
    p = os.environ.get("VASAI_EV_DB_PATH",
                       str(Path(__file__).parent.parent / "data" / "vasai_evidence.db"))
    return Path(p)


def _get_conn() -> sqlite3.Connection:
    path = str(_ev_db_path())
    with _lock:
        conn = _conn_cache.get(path)
        if conn is None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            _conn_cache[path] = conn
        return conn


def initialize() -> None:
    conn = _get_conn()
    with _lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id            TEXT PRIMARY KEY,
                event_id      TEXT NOT NULL DEFAULT '',
                decision_id   TEXT NOT NULL DEFAULT '',
                evidence_type TEXT NOT NULL,
                content       TEXT NOT NULL DEFAULT '{}',
                source        TEXT NOT NULL DEFAULT '',
                confidence    REAL NOT NULL DEFAULT 1.0,
                created_at    TEXT NOT NULL,
                hash          TEXT NOT NULL,
                prev_hash     TEXT NOT NULL DEFAULT 'GENESIS'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ev_seq (
                date_key TEXT PRIMARY KEY,
                counter  INTEGER NOT NULL DEFAULT 0
            )
        """)


def _next_id(conn: sqlite3.Connection) -> str:
    key = datetime.now(timezone.utc).strftime("%Y%m%d")
    row = conn.execute("SELECT counter FROM ev_seq WHERE date_key=?", (key,)).fetchone()
    n = (row["counter"] + 1) if row else 1
    conn.execute(
        "INSERT INTO ev_seq(date_key,counter) VALUES(?,?) "
        "ON CONFLICT(date_key) DO UPDATE SET counter=excluded.counter",
        (key, n),
    )
    return f"EV{key}_{n:06d}"


def _hash_fields(fields: list) -> str:
    parts = [f if f is not None else "" for f in fields]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _latest_hash(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT hash FROM evidence ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["hash"] if row else "GENESIS"


class EvidenceLedger:
    """判断根拠を記録・追跡するLedger。"""

    def add_evidence(
        self,
        event_id: str,
        decision_id: str,
        evidence_type: str,
        content: dict,
        source: str,
        confidence: float = 1.0,
    ) -> str:
        """根拠を記録してevidence_idを返す。"""
        if evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f"evidence_type must be one of {EVIDENCE_TYPES}")

        initialize()
        created_at = datetime.now(timezone.utc).isoformat()
        content_str = json.dumps(content, ensure_ascii=False, sort_keys=True)
        conf = max(0.0, min(1.0, confidence))

        conn = _get_conn()
        with _lock:
            conn.execute("BEGIN IMMEDIATE")
            try:
                ev_id = _next_id(conn)
                prev_hash = _latest_hash(conn)
                h = _hash_fields([ev_id, event_id, decision_id, evidence_type,
                                  content_str, source, str(conf), created_at, prev_hash])
                conn.execute(
                    "INSERT INTO evidence VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (ev_id, event_id, decision_id, evidence_type,
                     content_str, source, conf, created_at, h, prev_hash),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
        return ev_id

    def get_decision_chain(self, decision_id: str) -> dict:
        """Decision→Evidence→Approval→Result の全チェーンを返す。"""
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM evidence WHERE decision_id=? ORDER BY id ASC",
            (decision_id,),
        ).fetchall()

        evidences = []
        for row in rows:
            d = dict(row)
            d["content"] = json.loads(d["content"])
            evidences.append(d)

        # 根拠を種別ごとに整理
        by_type: dict[str, list] = {t: [] for t in EVIDENCE_TYPES}
        for ev in evidences:
            t = ev["evidence_type"]
            if t in by_type:
                by_type[t].append(ev)

        return {
            "decision_id":   decision_id,
            "total_evidence": len(evidences),
            "chain":          evidences,
            "by_type":        by_type,
            "facts":          by_type["FACT"],
            "assumptions":    by_type["ASSUMPTION"],
            "constraints":    by_type["CONSTRAINT"],
            "intents":        by_type["INTENT"],
        }

    def why_was_this_decided(self, event_id: str) -> str:
        """自然言語で判断理由を説明する。"""
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM evidence WHERE event_id=? ORDER BY id ASC",
            (event_id,),
        ).fetchall()

        if not rows:
            return f"event_id={event_id} に対する根拠の記録が見つかりません。"

        parts = [f"【判断根拠: event_id={event_id}】"]
        for row in rows:
            d = dict(row)
            c = json.loads(d["content"])
            label = {"FACT": "事実", "ASSUMPTION": "前提", "CONSTRAINT": "制約",
                     "INTENT": "意図"}.get(d["evidence_type"], d["evidence_type"])
            desc = c.get("description", c.get("summary", str(c)))
            conf_pct = int(d["confidence"] * 100)
            parts.append(f"  [{label}({conf_pct}%)] {desc} (出典: {d['source']})")

        return "\n".join(parts)

    def verify_chain(self) -> bool:
        """evidence全件のhashチェーン検証。"""
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM evidence ORDER BY id ASC"
        ).fetchall()
        if not rows:
            return True
        prev = "GENESIS"
        for row in rows:
            d = dict(row)
            if d["prev_hash"] != prev:
                return False
            expected = _hash_fields([
                d["id"], d["event_id"], d["decision_id"], d["evidence_type"],
                d["content"], d["source"], str(d["confidence"]),
                d["created_at"], d["prev_hash"],
            ])
            if expected != d["hash"]:
                return False
            prev = d["hash"]
        return True

    def list_by_event(self, event_id: str) -> list[dict]:
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM evidence WHERE event_id=? ORDER BY id ASC",
            (event_id,),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["content"] = json.loads(d["content"])
            result.append(d)
        return result

    def list_by_decision(self, decision_id: str) -> list[dict]:
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM evidence WHERE decision_id=? ORDER BY id ASC",
            (decision_id,),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["content"] = json.loads(d["content"])
            result.append(d)
        return result
