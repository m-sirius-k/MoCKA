import sqlite3
import json
import os
import hashlib
from datetime import datetime, UTC
from typing import Dict, Any, Optional


LEDGER_TABLE = "audit_ledger_event"
CONTRACT_VERSION = "mocka.audit.v1"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {LEDGER_TABLE} (
        event_id TEXT PRIMARY KEY,
        chain_hash TEXT NOT NULL,
        prev_event_id TEXT,
        event_content TEXT NOT NULL,
        contract_version TEXT NOT NULL DEFAULT '{CONTRACT_VERSION}',
        created_at TEXT NOT NULL
    )
    """)
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{LEDGER_TABLE}_prev ON {LEDGER_TABLE}(prev_event_id)"
    )


class AuditWriter:
    """
    Writer is the only place that is allowed to:
      - choose prev_event_id (current TIP)
      - compute event_id
      - compute chain_hash
      - set created_at
    Use write_payload() for normal operation.

    write_event() remains for backward compatibility (legacy precomputed events).
    """

    def __init__(self, db_path: str):
        if not db_path:
            raise ValueError("db_path is required")
        self._db_path = db_path.strip()

    def open(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        _ensure_schema(conn)
        return conn

    def _get_current_tip(self, conn: sqlite3.Connection) -> Optional[str]:
        cur = conn.cursor()
        cur.execute(
            f"SELECT event_id FROM {LEDGER_TABLE} ORDER BY created_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        return row[0] if row else None

    def _canonical_json(self, obj: Dict[str, Any]) -> str:
        return json.dumps(obj, ensure_ascii=True, separators=(",", ":"))

    def write_payload(
        self,
        payload: Dict[str, Any],
        note: str = "",
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        Normal path.
        payload: arbitrary dict (type, fields...)
        Returns the full stored event dict.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")

        created_at = _utc_now_iso()

        # Ensure created_at is part of event_content, so event_id is time-unique.
        payload_with_time = dict(payload)
        payload_with_time.setdefault("created_at", created_at)

        event_content = self._canonical_json(payload_with_time)
        event_id = hashlib.sha256(event_content.encode("utf-8")).hexdigest()

        conn = self.open()
        try:
            prev_event_id = self._get_current_tip(conn)

            chain_material = (prev_event_id or "") + event_id
            chain_hash = hashlib.sha256(chain_material.encode("utf-8")).hexdigest()

            event = {
                "event_id": event_id,
                "chain_hash": chain_hash,
                "prev_event_id": prev_event_id,
                "event_content": event_content,
                "contract_version": CONTRACT_VERSION,
                "created_at": created_at,
                "note": note,
            }

            conn.execute(f"""
                INSERT INTO {LEDGER_TABLE}
                (event_id, chain_hash, prev_event_id, event_content, contract_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                chain_hash,
                prev_event_id,
                event_content,
                CONTRACT_VERSION,
                created_at,
            ))

            if commit:
                conn.commit()

            return event
        finally:
            conn.close()

    def write_event(
        self,
        event: Dict[str, Any],
        note: str = "",
        commit: bool = True
    ) -> None:
        """
        Legacy path.
        Expects precomputed event_id/chain_hash/prev_event_id etc.
        Use write_payload() unless you intentionally preserve legacy behavior.
        """
        if not isinstance(event, dict):
            raise TypeError("event must be a dict")

        event_id = str(event.get("event_id", "")).strip()
        if not event_id:
            raise ValueError("event.event_id is required")

        chain_hash = str(event.get("chain_hash", "")).strip()
        if not chain_hash:
            raise ValueError("event.chain_hash is required")

        created_at = str(event.get("created_at", "")).strip() or _utc_now_iso()

        prev_event_id_raw = event.get("prev_event_id")
        prev_event_id = (
            str(prev_event_id_raw).strip()
            if prev_event_id_raw is not None else None
        )

        event_content = str(event.get("event_content", "")).strip()
        if not event_content:
            # fallback: store canonical json of whole event
            event_content = self._canonical_json(event)

        conn = self.open()
        try:
            conn.execute(f"""
                INSERT INTO {LEDGER_TABLE}
                (event_id, chain_hash, prev_event_id, event_content, contract_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                chain_hash,
                prev_event_id,
                event_content,
                CONTRACT_VERSION,
                created_at,
            ))

            if commit:
                conn.commit()
        finally:
            conn.close()