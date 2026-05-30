"""
vasAI Core: append-only SQLite event store with SHA-256 hash chain.
"""
import sqlite3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "vasai_events.db"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA encoding='UTF-8'")
    return conn


def initialize_db() -> None:
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id              TEXT PRIMARY KEY,
                when_ts         TEXT NOT NULL,
                who_actor       TEXT NOT NULL,
                what_type       TEXT NOT NULL,
                where_component TEXT,
                why_purpose     TEXT,
                how_trigger     TEXT,
                content         TEXT,
                prev_hash       TEXT,
                hash            TEXT NOT NULL,
                caliber_id      TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS id_counter (
                date_key TEXT PRIMARY KEY,
                counter  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def _next_event_id(conn: sqlite3.Connection) -> str:
    date_key = datetime.now(timezone.utc).strftime("%Y%m%d")
    row = conn.execute(
        "SELECT counter FROM id_counter WHERE date_key = ?", (date_key,)
    ).fetchone()
    counter = (row["counter"] + 1) if row else 1
    conn.execute(
        "INSERT INTO id_counter (date_key, counter) VALUES (?, ?) "
        "ON CONFLICT(date_key) DO UPDATE SET counter = excluded.counter",
        (date_key, counter),
    )
    return f"E{date_key}_{counter:03d}"


def _compute_hash(event_id: str, when_ts: str, who: str, what: str,
                  content: str, prev_hash: str) -> str:
    raw = f"{event_id}|{when_ts}|{who}|{what}|{content}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_latest_hash(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT hash FROM events ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["hash"] if row else "GENESIS"


def append_event(
    who_actor: str,
    what_type: str,
    where_component: str = "",
    why_purpose: str = "",
    how_trigger: str = "",
    content: dict | None = None,
    caliber_id: str = "",
) -> str:
    """Append a new event. Returns the generated event ID."""
    initialize_db()
    when_ts = datetime.now(timezone.utc).isoformat()
    content_str = json.dumps(content or {}, ensure_ascii=False)

    with _get_connection() as conn:
        event_id = _next_event_id(conn)
        prev_hash = _get_latest_hash(conn)
        event_hash = _compute_hash(event_id, when_ts, who_actor, what_type,
                                   content_str, prev_hash)
        conn.execute(
            """INSERT INTO events
               (id, when_ts, who_actor, what_type, where_component,
                why_purpose, how_trigger, content, prev_hash, hash, caliber_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, when_ts, who_actor, what_type, where_component,
             why_purpose, how_trigger, content_str, prev_hash,
             event_hash, caliber_id),
        )
        conn.commit()
    return event_id


def get_event(event_id: str) -> dict | None:
    initialize_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["content"] = json.loads(d["content"])
    return d


def list_events(limit: int = 50, what_type: str = "") -> list[dict]:
    initialize_db()
    with _get_connection() as conn:
        if what_type:
            rows = conn.execute(
                "SELECT * FROM events WHERE what_type = ? ORDER BY id DESC LIMIT ?",
                (what_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["content"] = json.loads(d["content"])
        result.append(d)
    return result


def verify_chain() -> tuple[bool, str]:
    """Verify the full hash chain. Returns (is_valid, message)."""
    initialize_db()
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY id ASC"
        ).fetchall()

    if not rows:
        return True, "Chain is empty (valid)"

    prev_hash = "GENESIS"
    for row in rows:
        d = dict(row)
        expected = _compute_hash(
            d["id"], d["when_ts"], d["who_actor"], d["what_type"],
            d["content"], prev_hash,
        )
        if expected != d["hash"]:
            return False, f"Chain broken at event {d['id']}"
        if d["prev_hash"] != prev_hash:
            return False, f"prev_hash mismatch at event {d['id']}"
        prev_hash = d["hash"]

    return True, f"Chain intact ({len(rows)} events verified)"
