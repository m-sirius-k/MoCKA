"""
vasAI Core: append-only SQLite event store with SHA-256 hash chain.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.models import MovementStage

_DEFAULT_DB = Path(__file__).parent.parent / "data" / "vasai_events.db"


def _db_path() -> Path:
    import os
    p = os.environ.get("VASAI_DB_PATH", str(_DEFAULT_DB))
    return Path(p)


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id              TEXT PRIMARY KEY,
                when_ts         TEXT NOT NULL,
                who_actor       TEXT NOT NULL,
                what_type       TEXT NOT NULL,
                where_component TEXT DEFAULT '',
                why_purpose     TEXT DEFAULT '',
                how_trigger     TEXT DEFAULT '',
                content         TEXT DEFAULT '{}',
                prev_hash       TEXT DEFAULT 'GENESIS',
                hash            TEXT NOT NULL,
                caliber_id      TEXT DEFAULT '',
                stage           TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS id_seq (
                date_key TEXT PRIMARY KEY,
                counter  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def _next_id(conn: sqlite3.Connection) -> str:
    key = datetime.now(timezone.utc).strftime("%Y%m%d")
    row = conn.execute("SELECT counter FROM id_seq WHERE date_key=?", (key,)).fetchone()
    n = (row["counter"] + 1) if row else 1
    conn.execute(
        "INSERT INTO id_seq(date_key,counter) VALUES(?,?) "
        "ON CONFLICT(date_key) DO UPDATE SET counter=excluded.counter",
        (key, n),
    )
    return f"E{key}_{n:03d}"


def _compute_hash(fields: list[str]) -> str:
    raw = "|".join(fields)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_latest_hash(conn: Optional[sqlite3.Connection] = None) -> str:
    close_after = conn is None
    if conn is None:
        initialize()
        conn = _connect()
    row = conn.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    result = row["hash"] if row else "GENESIS"
    if close_after:
        conn.close()
    return result


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

    with _connect() as conn:
        event_id = _next_id(conn)
        prev_hash = get_latest_hash(conn)
        h = _compute_hash([
            event_id, when_ts, who_actor, what_type,
            where_component, why_purpose, how_trigger,
            content_str, prev_hash, caliber_id,
        ])
        conn.execute(
            "INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (event_id, when_ts, who_actor, what_type, where_component,
             why_purpose, how_trigger, content_str, prev_hash, h,
             caliber_id, stage),
        )
        conn.commit()
    return event_id


def get(event_id: str) -> Optional[dict]:
    initialize()
    with _connect() as conn:
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

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["content"] = json.loads(d["content"])
        result.append(d)
    return result


def verify_chain() -> bool:
    initialize()
    with _connect() as conn:
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
            d["where_component"], d["why_purpose"], d["how_trigger"],
            d["content"], d["prev_hash"], d["caliber_id"],
        ])
        if expected != d["hash"]:
            return False
        prev = d["hash"]
    return True


def get_stage_counts() -> dict[str, int]:
    initialize()
    counts = {s.value: 0 for s in MovementStage}
    with _connect() as conn:
        rows = conn.execute(
            "SELECT stage, COUNT(*) as c FROM events WHERE stage!='' GROUP BY stage"
        ).fetchall()
    for row in rows:
        if row["stage"] in counts:
            counts[row["stage"]] = row["c"]
    return counts
