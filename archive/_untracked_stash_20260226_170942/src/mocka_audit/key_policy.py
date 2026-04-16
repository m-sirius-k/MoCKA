import sqlite3
from datetime import datetime, UTC
from typing import Optional, Tuple

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # expecting ISO8601 with timezone, but tolerate Z-less
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def get_key_state(key_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    returns (status, valid_from, valid_to) or (None,None,None) if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT status, valid_from, valid_to FROM key_metadata WHERE key_id=?",
        (key_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return (None, None, None)
    return (row[0], row[1], row[2])


def assert_key_active(key_id: str) -> None:
    status, valid_from, valid_to = get_key_state(key_id)

    if status is None:
        raise RuntimeError(f"REJECTED: key not registered: {key_id}")

    if status != "active":
        raise RuntimeError(f"REJECTED: key not active: {key_id} status={status}")

    now = datetime.now(UTC)

    vf = _parse_iso(valid_from)
    if vf is not None and vf.tzinfo is None:
        vf = vf.replace(tzinfo=UTC)
    if vf is not None and now < vf:
        raise RuntimeError(f"REJECTED: key not yet valid: {key_id} valid_from={valid_from}")

    vt = _parse_iso(valid_to)
    if vt is not None and vt.tzinfo is None:
        vt = vt.replace(tzinfo=UTC)
    if vt is not None and now >= vt:
        raise RuntimeError(f"REJECTED: key expired: {key_id} valid_to={valid_to}")