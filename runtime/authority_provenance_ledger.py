"""
MoCKA 3.0 — Authority Provenance Ledger
authority_provenance_ledger.py

責務:
  Execution Decision に紐付く Authority Context の provenance を記録する。

  DESIGN DECISIONS 用の decision_ledger.jsonl とは別に、
  EXECUTION DECISIONS 用の authority_provenance_ledger.jsonl を新設。

  - Write: Authority Context → JSONL record
  - Persist: Append to authority_provenance_ledger.jsonl
  - Read-back: Load and verify persisted record
  - Consistency: In-memory state == Persisted state (no mutation)

M3 Integration Phase:
  - STEP 5: Authority Provenance Recording
  - Sandbox only, production ledger untouched
  - Authority state at T_decision (immutable historical record)
  - Authority state at T_execution/revalidation (current state reference)
  - No retroactive mutation when authority is revoked later
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import asdict


class AuthorityProvenanceRecord:
    """Single authority provenance record."""

    def __init__(
        self,
        decision_id: str,
        authority_context_id: str,
        authority_id: str,
        verification_state_at_decision: str,
        authority_lifecycle_state: str,
        decision_timestamp: str,
        provenance_reference: Optional[str] = None,
        execution_result_status: Optional[str] = None,
        revocation_reference: Optional[str] = None,
    ):
        self.decision_id = decision_id
        self.authority_context_id = authority_context_id
        self.authority_id = authority_id
        self.verification_state_at_decision = verification_state_at_decision
        self.authority_lifecycle_state = authority_lifecycle_state
        self.decision_timestamp = decision_timestamp
        self.provenance_reference = provenance_reference
        self.execution_result_status = execution_result_status
        self.revocation_reference = revocation_reference
        self.recorded_at = datetime.utcnow().isoformat()
        self.record_version = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSONL storage."""
        return {
            "decision_id": self.decision_id,
            "authority_context_id": self.authority_context_id,
            "authority_id": self.authority_id,
            "verification_state_at_decision": self.verification_state_at_decision,
            "authority_lifecycle_state": self.authority_lifecycle_state,
            "decision_timestamp": self.decision_timestamp,
            "provenance_reference": self.provenance_reference,
            "execution_result_status": self.execution_result_status,
            "revocation_reference": self.revocation_reference,
            "recorded_at": self.recorded_at,
            "record_version": self.record_version,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthorityProvenanceRecord":
        """Deserialize from dict (loaded from JSONL)."""
        record = AuthorityProvenanceRecord(
            decision_id=data["decision_id"],
            authority_context_id=data["authority_context_id"],
            authority_id=data["authority_id"],
            verification_state_at_decision=data["verification_state_at_decision"],
            authority_lifecycle_state=data["authority_lifecycle_state"],
            decision_timestamp=data["decision_timestamp"],
            provenance_reference=data.get("provenance_reference"),
            execution_result_status=data.get("execution_result_status"),
            revocation_reference=data.get("revocation_reference"),
        )
        record.recorded_at = data.get("recorded_at", record.recorded_at)
        record.record_version = data.get("record_version", "1.0")
        return record

    def __eq__(self, other) -> bool:
        """Compare records (for consistency verification)."""
        if not isinstance(other, AuthorityProvenanceRecord):
            return False
        return (
            self.decision_id == other.decision_id
            and self.authority_context_id == other.authority_context_id
            and self.authority_id == other.authority_id
            and self.verification_state_at_decision
            == other.verification_state_at_decision
            and self.authority_lifecycle_state == other.authority_lifecycle_state
            and self.decision_timestamp == other.decision_timestamp
            and self.provenance_reference == other.provenance_reference
            and self.execution_result_status == other.execution_result_status
            and self.revocation_reference == other.revocation_reference
            and self.record_version == other.record_version
        )


class AuthorityProvenanceLedger:
    """Authority Provenance Ledger — JSONL append-only storage."""

    def __init__(self, ledger_path: Optional[Path] = None):
        """
        Initialize ledger.

        Args:
            ledger_path: Path to authority_provenance_ledger.jsonl
                        Default: data/decisions/authority_provenance_ledger.jsonl
        """
        if ledger_path is None:
            ledger_path = Path(__file__).parent.parent / "data" / "decisions" / "authority_provenance_ledger.jsonl"
        self.ledger_path = Path(ledger_path)
        # Ensure parent directory exists
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def write_record(self, record: AuthorityProvenanceRecord) -> bool:
        """
        Write record to ledger (append-only).

        Args:
            record: AuthorityProvenanceRecord to write

        Returns:
            True if write successful
        """
        try:
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                json_line = json.dumps(record.to_dict(), ensure_ascii=False)
                f.write(json_line + "\n")
            return True
        except Exception as e:
            print(f"ERROR writing to ledger: {e}")
            return False

    def read_record(self, decision_id: str) -> Optional[AuthorityProvenanceRecord]:
        """
        Read record from ledger by decision_id (linear search, O(n)).

        Args:
            decision_id: decision_id to search for

        Returns:
            AuthorityProvenanceRecord if found, None otherwise
        """
        if not self.ledger_path.exists():
            return None

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("decision_id") == decision_id:
                        return AuthorityProvenanceRecord.from_dict(data)
            return None
        except Exception as e:
            print(f"ERROR reading from ledger: {e}")
            return None

    def read_all_records(self) -> list:
        """
        Read all records from ledger.

        Returns:
            List of AuthorityProvenanceRecord objects
        """
        records = []
        if not self.ledger_path.exists():
            return records

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    records.append(AuthorityProvenanceRecord.from_dict(data))
            return records
        except Exception as e:
            print(f"ERROR reading all records from ledger: {e}")
            return records

    def verify_record_persisted(self, record: AuthorityProvenanceRecord) -> bool:
        """
        Verify that record was persisted correctly.

        Reads back from storage and compares with original.

        Args:
            record: Record that was written

        Returns:
            True if persisted record matches original (ignoring recorded_at timestamp precision)
        """
        persisted = self.read_record(record.decision_id)
        if persisted is None:
            return False

        # Compare all fields except recorded_at (timestamp precision may vary)
        return (
            persisted.decision_id == record.decision_id
            and persisted.authority_context_id == record.authority_context_id
            and persisted.authority_id == record.authority_id
            and persisted.verification_state_at_decision
            == record.verification_state_at_decision
            and persisted.authority_lifecycle_state == record.authority_lifecycle_state
            and persisted.decision_timestamp == record.decision_timestamp
            and persisted.provenance_reference == record.provenance_reference
            and persisted.execution_result_status == record.execution_result_status
            and persisted.revocation_reference == record.revocation_reference
        )
