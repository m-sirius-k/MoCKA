"""
vasAI Core: HMAC-SHA256 audit chain — evolved from MoCKA ledger.json.
"""
import hashlib
import hmac
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.event_store import _get_connection, initialize_db

_SEAL_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_seals (
        seal_id     TEXT PRIMARY KEY,
        sealed_at   TEXT NOT NULL,
        event_count INTEGER NOT NULL,
        last_hash   TEXT NOT NULL,
        signature   TEXT NOT NULL
    )
"""

_SIG_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_signatures (
        sig_id      TEXT PRIMARY KEY,
        event_id    TEXT NOT NULL,
        signed_at   TEXT NOT NULL,
        payload     TEXT NOT NULL,
        prev_sig    TEXT NOT NULL,
        signature   TEXT NOT NULL
    )
"""

_HMAC_KEY_ENV = "VASAI_HMAC_KEY"


def _get_hmac_key() -> bytes:
    import os
    key = os.environ.get(_HMAC_KEY_ENV, "vasai-default-dev-key-change-in-prod")
    return key.encode("utf-8")


def _hmac_sign(payload: str) -> str:
    return hmac.new(_get_hmac_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _init_audit_tables() -> None:
    initialize_db()
    with _get_connection() as conn:
        conn.execute(_SEAL_TABLE)
        conn.execute(_SIG_TABLE)
        conn.commit()


def sign_event(event_id: str, event_payload: dict) -> str:
    """Sign an event. Returns sig_id."""
    _init_audit_tables()
    signed_at = datetime.now(timezone.utc).isoformat()
    payload_str = json.dumps(event_payload, sort_keys=True, ensure_ascii=False)

    with _get_connection() as conn:
        row = conn.execute(
            "SELECT signature FROM audit_signatures ORDER BY sig_id DESC LIMIT 1"
        ).fetchone()
        prev_sig = row["signature"] if row else "GENESIS_SIG"

        full_payload = f"{event_id}|{signed_at}|{payload_str}|{prev_sig}"
        signature = _hmac_sign(full_payload)
        sig_id = f"SIG_{event_id}"

        conn.execute(
            "INSERT OR REPLACE INTO audit_signatures "
            "(sig_id, event_id, signed_at, payload, prev_sig, signature) "
            "VALUES (?,?,?,?,?,?)",
            (sig_id, event_id, signed_at, payload_str, prev_sig, signature),
        )
        conn.commit()
    return sig_id


def verify_signature(sig_id: str) -> bool:
    """Verify a single signature."""
    _init_audit_tables()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM audit_signatures WHERE sig_id = ?", (sig_id,)
        ).fetchone()
    if row is None:
        return False
    d = dict(row)
    full_payload = f"{d['event_id']}|{d['signed_at']}|{d['payload']}|{d['prev_sig']}"
    expected = _hmac_sign(full_payload)
    return hmac.compare_digest(expected, d["signature"])


def verify_chain() -> tuple[bool, str]:
    """Verify the full signature chain."""
    _init_audit_tables()
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_signatures ORDER BY sig_id ASC"
        ).fetchall()

    if not rows:
        return True, "Audit chain empty (valid)"

    prev_sig = "GENESIS_SIG"
    for row in rows:
        d = dict(row)
        if d["prev_sig"] != prev_sig:
            return False, f"Chain broken at sig {d['sig_id']}: prev_sig mismatch"
        full_payload = f"{d['event_id']}|{d['signed_at']}|{d['payload']}|{d['prev_sig']}"
        expected = _hmac_sign(full_payload)
        if not hmac.compare_digest(expected, d["signature"]):
            return False, f"Invalid signature at {d['sig_id']}"
        prev_sig = d["signature"]

    return True, f"Audit chain intact ({len(rows)} signatures verified)"


def seal(note: str = "") -> dict:
    """Seal the current state — timestamp + count + last_hash + signature."""
    _init_audit_tables()
    sealed_at = datetime.now(timezone.utc).isoformat()

    with _get_connection() as conn:
        count_row = conn.execute("SELECT COUNT(*) as c FROM events").fetchone()
        hash_row = conn.execute(
            "SELECT hash FROM events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        event_count = count_row["c"] if count_row else 0
        last_hash = hash_row["hash"] if hash_row else "EMPTY"

        seal_payload = f"SEAL|{sealed_at}|{event_count}|{last_hash}|{note}"
        signature = _hmac_sign(seal_payload)
        seal_id = f"SEAL_{sealed_at[:10].replace('-','')}_{event_count}"

        conn.execute(
            "INSERT OR REPLACE INTO audit_seals "
            "(seal_id, sealed_at, event_count, last_hash, signature) "
            "VALUES (?,?,?,?,?)",
            (seal_id, sealed_at, event_count, last_hash, signature),
        )
        conn.commit()

    return {
        "seal_id": seal_id,
        "sealed_at": sealed_at,
        "event_count": event_count,
        "last_hash": last_hash,
        "signature": signature,
    }


def get_audit_report() -> dict:
    _init_audit_tables()
    chain_valid, chain_msg = verify_chain()
    with _get_connection() as conn:
        event_count = conn.execute("SELECT COUNT(*) as c FROM events").fetchone()["c"]
        sig_count = conn.execute(
            "SELECT COUNT(*) as c FROM audit_signatures"
        ).fetchone()["c"]
        seals = conn.execute(
            "SELECT * FROM audit_seals ORDER BY sealed_at DESC LIMIT 5"
        ).fetchall()

    return {
        "chain_valid": chain_valid,
        "chain_message": chain_msg,
        "total_events": event_count,
        "total_signatures": sig_count,
        "recent_seals": [dict(s) for s in seals],
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
    }
