import sqlite3
import hashlib
import json
from datetime import datetime, UTC
from typing import Dict, Any
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.mocka_audit.audit_writer import AuditWriter

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def _get_last_event(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT event_id, chain_hash FROM audit_ledger_event ORDER BY rowid DESC LIMIT 1"
    )
    row = cur.fetchone()
    if not row:
        return None, None
    return row[0], row[1]


def revoke_key_with_audit_event(key_id: str, reason: str) -> None:

    created_at = datetime.now(UTC).isoformat()

    payload: Dict[str, Any] = {
        "type": "key_revocation",
        "key_id": key_id,
        "reason_text": reason,
        "revoked_at": created_at,
    }

    payload_json = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))

    event_id = hashlib.sha256(payload_json.encode()).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    prev_event_id, prev_chain_hash = _get_last_event(conn)

    base_chain = (prev_chain_hash or "") + event_id
    chain_hash = hashlib.sha256(base_chain.encode()).hexdigest()

    conn.close()

    event = {
        "event_id": event_id,
        "created_at": created_at,
        "prev_event_id": prev_event_id,
        "chain_hash": chain_hash,
        "event_content": payload_json,
        **payload,
    }

    writer = AuditWriter(db_path=DB_PATH)
    writer.write_event(
        event=event,
        note="NOTE: key revoked and sealed into audit chain",
        commit=True,
    )

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT key_id FROM key_revocation WHERE key_id = ?",
            (key_id,),
        )
        exists = cur.fetchone()

        if exists:
            print("INFO: key already revoked. Skipping DB insert.")
        else:
            cur.execute(
                """
                INSERT INTO key_revocation
                (key_id, revoked_at, reason_code, reason_text, revoked_by, audit_event_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key_id,
                    created_at,
                    "MANUAL_REVOKE",
                    reason,
                    "phase13-script",
                    event_id,
                ),
            )
            conn.commit()
            print("OK: key revoked with audit_event_id =", event_id)

    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python revoke_key_with_audit_event.py <key_id> <reason>")
        raise SystemExit(1)

    revoke_key_with_audit_event(sys.argv[1], sys.argv[2])