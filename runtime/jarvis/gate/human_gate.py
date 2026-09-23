import sqlite3
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from runtime.jarvis.record.adapter.ledger_adapter import LedgerAdapter


class HumanGate:
    def __init__(self):
        self.status = "WAITING"
        self.ledger = LedgerAdapter()
        self._repo_root = Path(__file__).resolve().parent.parent.parent.parent
        self._db_path = str(self._repo_root / 'data' / 'mocka_events.db')

    def _get_conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_authorization_by_decision_id(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Lookup authorization_state by decision_id.
        Returns dict with authorization_id, status, etc., or None if not found.
        """
        try:
            conn = self._get_conn()
            row = conn.execute(
                'SELECT * FROM authorization_state WHERE decision_id = ? ORDER BY granted_at DESC LIMIT 1',
                (decision_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    def request(self, decision_id):
        """
        JARVIS request handler: receive decision_id and check authorization state.
        Returns status and authorization info if found, otherwise WAITING.
        """
        return {
            "decision_id": decision_id,
            "status": self.status,
            "authority": "human"
        }

    def receive_decision_and_authorize(self, decision_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        STEP 3: JARVIS-facing gate that checks authorization and returns authorization_id.

        Returns:
            (authorized: bool, reason: str, authorization_id: Optional[str])

        Fail-Closed:
        - authorization_state not found -> (False, "not_found", None)
        - status != APPROVED -> (False, "not_approved", None)
        - decision_id not in auth_state -> (False, "decision_id_mismatch", None)
        """
        auth_record = self._get_authorization_by_decision_id(decision_id)

        if not auth_record:
            return False, "authorization_not_found", None

        if auth_record.get('status') != 'APPROVED':
            return False, f"status_is_{auth_record.get('status')}_not_approved", None

        # Verify decision_id matches
        if auth_record.get('decision_id') != decision_id:
            return False, "decision_id_mismatch", None

        # Authorization valid - return authorization_id for T2 runtime
        return True, "authorized", auth_record.get('authorization_id')

    def approve(self, decision_id):
        self.status = "APPROVED"
        return self.ledger.record(
            decision_id,
            self.status
        )

    def reject(self, decision_id):
        self.status = "REJECTED"
        return self.ledger.record(
            decision_id,
            self.status
        )