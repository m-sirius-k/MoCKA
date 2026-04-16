import sqlite3
from typing import Dict, Optional


class AuditWriterV2:
    """
    DB schema fixed (confirmed):
      - event_id
      - chain_hash
      - previous_event_id
      - event_content
      - contract_version
      - created_at

    Canonical input keys (fixed):
      - event_id
      - previous_event_id
      - chain_hash
      - event_content
    """

    def __init__(self, db_path: str, table: str = "audit_ledger_event") -> None:
        self.db_path = db_path
        self.table = table

    def write_event(self, payload: Dict[str, Optional[str]]) -> None:
        event_id = payload.get("event_id")
        previous_event_id = payload.get("previous_event_id")
        chain_hash = payload.get("chain_hash")
        event_content = payload.get("event_content")

        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty str")
        if previous_event_id is not None and not isinstance(previous_event_id, str):
            raise ValueError("previous_event_id must be str or None")
        if not isinstance(chain_hash, str) or not chain_hash:
            raise ValueError("chain_hash must be non-empty str")
        if not isinstance(event_content, str):
            raise ValueError("event_content must be str")

        with sqlite3.connect(self.db_path) as conn:
            sql = (
                f"INSERT INTO {self.table} "
                f"(event_id, chain_hash, previous_event_id, event_content) "
                f"VALUES (?, ?, ?, ?);"
            )
            conn.execute(sql, (event_id, chain_hash, previous_event_id, event_content))
            conn.commit()
