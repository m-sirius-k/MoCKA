"""
vasAI Core: append-only SQLite event store with SHA-256 hash chain.
一接続維持 + isolation_level=None で高速・安全なトランザクション管理。
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.models import MovementStage

_DEFAULT_DB = Path(__file__).parent.parent / "data" / "vasai_events.db"
_lock = threading.Lock()
_conn_cache: dict[str, sqlite3.Connection] = {}


def _db_path() -> Path:
    import os
    p = os.environ.get("VASAI_DB_PATH", str(_DEFAULT_DB))
    return Path(p)


def _get_conn() -> sqlite3.Connection:
    """DBパスごとにコネクションをキャッシュ（スレッドセーフ）。"""
    path = str(_db_path())
    with _lock:
        conn = _conn_cache.get(path)
        if conn is None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, check_same_thread=False,
                                   isolation_level=None)  # autocommit mode
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            _conn_cache[path] = conn
        return conn


def _reset_conn() -> None:
    """テスト用: DBパスが変わった時にコネクションキャッシュをクリア。"""
    import os
    path = str(_db_path())
    with _lock:
        old = _conn_cache.pop(path, None)
        if old:
            try:
                old.close()
            except Exception:
                pass


def initialize() -> None:
    conn = _get_conn()
    with _lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id              TEXT PRIMARY KEY,
                when_ts         TEXT NOT NULL,
                who_actor       TEXT NOT NULL,
                what_type       TEXT NOT NULL,
                where_component TEXT NOT NULL DEFAULT '',
                why_purpose     TEXT NOT NULL DEFAULT '',
                how_trigger     TEXT NOT NULL DEFAULT '',
                content         TEXT NOT NULL DEFAULT '{}',
                prev_hash       TEXT NOT NULL DEFAULT 'GENESIS',
                hash            TEXT NOT NULL,
                caliber_id      TEXT NOT NULL DEFAULT '',
                stage           TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS id_seq (
                date_key TEXT PRIMARY KEY,
                counter  INTEGER NOT NULL DEFAULT 0
            )
        """)


def _next_id_unsafe(conn: sqlite3.Connection) -> str:
    key = datetime.now(timezone.utc).strftime("%Y%m%d")
    row = conn.execute("SELECT counter FROM id_seq WHERE date_key=?",
                       (key,)).fetchone()
    n = (row["counter"] + 1) if row else 1
    conn.execute(
        "INSERT INTO id_seq(date_key,counter) VALUES(?,?) "
        "ON CONFLICT(date_key) DO UPDATE SET counter=excluded.counter",
        (key, n),
    )
    return f"E{key}_{n:03d}"


def _compute_hash(fields: list) -> str:
    parts = [f if f is not None else "" for f in fields]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_latest_hash(conn: Optional[sqlite3.Connection] = None) -> str:
    c = conn or _get_conn()
    row = c.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    return row["hash"] if row else "GENESIS"


def append(
    who_actor: str,
    what_type: str,
    where_component: str = "",
    why_purpose: str = "",
    how_trigger: str = "",
    content: Optional[dict] = None,
    caliber_id: str = "",
    stage: str = "",
) -> str:
    initialize()
    when_ts = datetime.now(timezone.utc).isoformat()
    content_str = json.dumps(content or {}, ensure_ascii=False, sort_keys=True)
    wc = where_component or ""
    wp = why_purpose or ""
    ht = how_trigger or ""
    ci = caliber_id or ""
    st = stage or ""

    conn = _get_conn()
    with _lock:
        conn.execute("BEGIN IMMEDIATE")
        try:
            event_id = _next_id_unsafe(conn)
            prev_hash = get_latest_hash(conn)
            h = _compute_hash([event_id, when_ts, who_actor, what_type,
                               wc, wp, ht, content_str, prev_hash, ci])
            conn.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (event_id, when_ts, who_actor, what_type, wc, wp, ht,
                 content_str, prev_hash, h, ci, st),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return event_id


def get(event_id: str) -> Optional[dict]:
    initialize()
    conn = _get_conn()
    row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["content"] = json.loads(d["content"])
    return d


def list_events(
    limit: int = 50,
    what_type: str = "",
    caliber_id: str = "",
) -> list[dict]:
    initialize()
    query = "SELECT * FROM events WHERE 1=1"
    params: list = []
    if what_type:
        query += " AND what_type=?"
        params.append(what_type)
    if caliber_id:
        query += " AND caliber_id=?"
        params.append(caliber_id)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    conn = _get_conn()
    rows = conn.execute(query, params).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["content"] = json.loads(d["content"])
        result.append(d)
    return result


def verify_chain() -> bool:
    initialize()
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM events ORDER BY id ASC").fetchall()
    if not rows:
        return True
    prev = "GENESIS"
    for row in rows:
        d = dict(row)
        if d["prev_hash"] != prev:
            return False
        expected = _compute_hash([
            d["id"], d["when_ts"], d["who_actor"], d["what_type"],
            d["where_component"] or "", d["why_purpose"] or "",
            d["how_trigger"] or "", d["content"],
            d["prev_hash"], d["caliber_id"] or "",
        ])
        if expected != d["hash"]:
            return False
        prev = d["hash"]
    return True


def get_stage_counts() -> dict[str, int]:
    initialize()
    counts = {s.value: 0 for s in MovementStage}
    conn = _get_conn()
    rows = conn.execute(
        "SELECT stage, COUNT(*) as c FROM events WHERE stage!='' GROUP BY stage"
    ).fetchall()
    for row in rows:
        if row["stage"] in counts:
            counts[row["stage"]] = row["c"]
    return counts
