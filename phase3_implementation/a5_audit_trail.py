"""
HG-M3 Phase 3: Component A5 - Audit Trail Infrastructure

Implement audit ledger schema (immutable append-only)
Implement hash-chain structure for retroactive insertion detection
Implement retention policy configuration (5-year window)

Status: DESIGN LAYER ONLY (schema and structure)
Environment: SANDBOX ONLY
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class AuditLedgerEntry:
    """Single entry in immutable audit ledger"""

    def __init__(self, entry_id: str, action_type: str, actor: str, details: Dict,
                 previous_hash: Optional[str] = None):
        """
        Args:
            entry_id: Unique entry identifier
            action_type: Type of action (binding_test, validation, etc.)
            actor: Who performed the action
            details: Detailed action information
            previous_hash: Hash of previous entry (for chain)
        """
        self.entry_id = entry_id
        self.action_type = action_type
        self.actor = actor
        self.details = details
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.previous_hash = previous_hash

        # Calculate current hash
        self.current_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA256 hash of this entry"""
        entry_data = {
            "entry_id": self.entry_id,
            "action_type": self.action_type,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "details": self.details,
            "previous_hash": self.previous_hash
        }
        entry_json = json.dumps(entry_data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "entry_id": self.entry_id,
            "action_type": self.action_type,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True)


class ImmutableAuditLedger:
    """Immutable append-only audit ledger with hash-chain"""

    def __init__(self, ledger_file: str):
        """
        Args:
            ledger_file: Path to JSONL ledger file
        """
        self.ledger_file = ledger_file
        self.entries: List[AuditLedgerEntry] = []
        self.last_hash: Optional[str] = None
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing entries from ledger file"""
        try:
            with open(self.ledger_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        # Recreate entry object (verify hash on load)
                        entry = AuditLedgerEntry(
                            data["entry_id"],
                            data["action_type"],
                            data["actor"],
                            data["details"],
                            data["previous_hash"]
                        )
                        # Verify hash hasn't been modified
                        if entry.current_hash != data["current_hash"]:
                            raise ValueError(f"Hash mismatch for entry {data['entry_id']}")
                        self.entries.append(entry)
                        self.last_hash = entry.current_hash
        except FileNotFoundError:
            pass  # First time initialization

    def append_entry(self, entry_id: str, action_type: str, actor: str, details: Dict) -> AuditLedgerEntry:
        """
        Append new entry to ledger

        Args:
            entry_id: Unique entry identifier
            action_type: Type of action
            actor: Who performed action
            details: Action details

        Returns:
            New AuditLedgerEntry
        """
        entry = AuditLedgerEntry(
            entry_id,
            action_type,
            actor,
            details,
            self.last_hash
        )

        # Append to file (immutable)
        with open(self.ledger_file, 'a') as f:
            f.write(entry.to_json() + "\n")

        self.entries.append(entry)
        self.last_hash = entry.current_hash

        return entry

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify hash-chain integrity

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        for i, entry in enumerate(self.entries):
            # Verify current hash
            expected_hash = entry._calculate_hash()
            if entry.current_hash != expected_hash:
                issues.append(f"Entry {entry.entry_id}: hash mismatch (tampering detected)")

            # Verify chain link
            if i > 0:
                expected_previous = self.entries[i - 1].current_hash
                if entry.previous_hash != expected_previous:
                    issues.append(f"Entry {entry.entry_id}: chain broken (retroactive insertion detected)")

        return (len(issues) == 0, issues)

    def detect_retroactive_insertion(self) -> Optional[int]:
        """
        Detect if entry was inserted retroactively

        Returns:
            Index of first broken link (None if no insertion detected)
        """
        for i in range(1, len(self.entries)):
            expected_previous = self.entries[i - 1].current_hash
            if self.entries[i].previous_hash != expected_previous:
                return i - 1  # Chain broken before this entry
        return None

    def get_entry_by_id(self, entry_id: str) -> Optional[AuditLedgerEntry]:
        """Get entry by ID"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_entries_by_action_type(self, action_type: str) -> List[AuditLedgerEntry]:
        """Get all entries of specific action type"""
        return [e for e in self.entries if e.action_type == action_type]

    def get_entries_by_actor(self, actor: str) -> List[AuditLedgerEntry]:
        """Get all entries by specific actor"""
        return [e for e in self.entries if e.actor == actor]

    def export_json(self) -> str:
        """Export ledger as JSON"""
        return json.dumps([e.to_dict() for e in self.entries], indent=2, ensure_ascii=True)


class RetentionPolicy:
    """5-year retention policy configuration"""

    RETENTION_WINDOW_DAYS = 365 * 5  # 5 years

    def __init__(self, creation_date: datetime):
        """
        Args:
            creation_date: When the policy is created
        """
        self.creation_date = creation_date
        self.retention_until = creation_date + timedelta(days=self.RETENTION_WINDOW_DAYS)

    def is_expired(self, entry_date: datetime) -> bool:
        """Check if entry is expired"""
        return entry_date + timedelta(days=self.RETENTION_WINDOW_DAYS) < datetime.utcnow()

    def get_expiration_date(self) -> str:
        """Get when this policy expires"""
        return self.retention_until.isoformat() + "Z"

    def to_dict(self) -> Dict:
        return {
            "retention_window_days": self.RETENTION_WINDOW_DAYS,
            "creation_date": self.creation_date.isoformat() + "Z",
            "retention_until": self.retention_until.isoformat() + "Z",
            "scope": "sandbox_only"
        }


class AuditTrailManager:
    """Centralized audit trail management"""

    def __init__(self, ledger_file: str):
        """
        Args:
            ledger_file: Path to audit ledger JSONL file
        """
        self.ledger = ImmutableAuditLedger(ledger_file)
        self.retention_policy = RetentionPolicy(datetime.utcnow())

    def log_decision_binding_test(self, decision_id: str, q_decisions: Dict[str, str],
                                   result: str, operator: str = "Phase3System") -> AuditLedgerEntry:
        """Log decision binding test"""
        return self.ledger.append_entry(
            f"LOG_DEC_{decision_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "decision_binding_test",
            operator,
            {
                "decision_id": decision_id,
                "q_decisions": q_decisions,
                "result": result
            }
        )

    def log_evidence_validation_test(self, evidence_id: str, validation_result: str,
                                      operator: str = "Phase3System") -> AuditLedgerEntry:
        """Log evidence validation test"""
        return self.ledger.append_entry(
            f"LOG_EVD_{evidence_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "evidence_validation_test",
            operator,
            {
                "evidence_id": evidence_id,
                "validation_result": validation_result
            }
        )

    def log_authority_registration(self, authority_id: str, snapshot_timestamp: str,
                                    operator: str = "Phase3System") -> AuditLedgerEntry:
        """Log authority registration"""
        return self.ledger.append_entry(
            f"LOG_AUT_{authority_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "authority_registration",
            operator,
            {
                "authority_id": authority_id,
                "snapshot_timestamp": snapshot_timestamp
            }
        )

    def log_failure_scenario_test(self, failure_pattern: str, escalation_id: str,
                                   operator: str = "Phase3System") -> AuditLedgerEntry:
        """Log failure scenario test"""
        return self.ledger.append_entry(
            f"LOG_FAIL_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{failure_pattern}",
            "failure_scenario_test",
            operator,
            {
                "failure_pattern": failure_pattern,
                "escalation_id": escalation_id
            }
        )

    def log_rollback_test(self, checkpoint_id: str, result: str,
                         operator: str = "Phase3System") -> AuditLedgerEntry:
        """Log rollback test"""
        return self.ledger.append_entry(
            f"LOG_RBCK_{checkpoint_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "rollback_test",
            operator,
            {
                "checkpoint_id": checkpoint_id,
                "rollback_result": result
            }
        )

    def verify_trail_integrity(self) -> Tuple[bool, List[str]]:
        """Verify audit trail integrity"""
        return self.ledger.verify_integrity()

    def export_audit_report(self) -> Dict:
        """Export comprehensive audit report"""
        is_valid, issues = self.verify_trail_integrity()
        retroactive_insert = self.ledger.detect_retroactive_insertion()

        return {
            "audit_report": {
                "total_entries": len(self.ledger.entries),
                "integrity_valid": is_valid,
                "integrity_issues": issues,
                "retroactive_insertion_detected": retroactive_insert is not None,
                "retroactive_insertion_at_index": retroactive_insert,
                "retention_policy": self.retention_policy.to_dict(),
                "last_entry_hash": self.ledger.last_hash
            }
        }


# Example usage
if __name__ == "__main__":
    print("Audit Trail Infrastructure - Immutable Ledger")
    print("=" * 60)

    # Initialize audit trail manager
    manager = AuditTrailManager("/tmp/test_audit_ledger.jsonl")

    # Log various actions
    print("\nLogging actions:")

    entry1 = manager.log_decision_binding_test(
        "DEC_001",
        {"Q1": "B", "Q2": "A", "Q3": "A", "Q4": "C", "Q5": "C", "Q6": "C"},
        "VALID"
    )
    print(f"  1. Decision binding: {entry1.entry_id}")

    entry2 = manager.log_evidence_validation_test(
        "EVD_001",
        "PASS"
    )
    print(f"  2. Evidence validation: {entry2.entry_id}")

    entry3 = manager.log_authority_registration(
        "AUT_001",
        "2026-09-18T08:00:00Z"
    )
    print(f"  3. Authority registration: {entry3.entry_id}")

    entry4 = manager.log_failure_scenario_test(
        "EVIDENCE_MISSING",
        "ESC_20260918_001"
    )
    print(f"  4. Failure scenario: {entry4.entry_id}")

    entry5 = manager.log_rollback_test(
        "CP1_20260918_001",
        "SUCCESS"
    )
    print(f"  5. Rollback test: {entry5.entry_id}")

    # Verify integrity
    print("\n" + "=" * 60)
    print("Integrity Verification:")
    is_valid, issues = manager.verify_trail_integrity()
    print(f"  Valid: {is_valid}")
    if issues:
        print(f"  Issues: {issues}")
    else:
        print("  No issues detected")

    # Export report
    print("\n" + "=" * 60)
    print("Audit Report:")
    report = manager.export_audit_report()
    print(json.dumps(report, indent=2, ensure_ascii=True))

    # Cleanup
    import os
    if os.path.exists("/tmp/test_audit_ledger.jsonl"):
        os.remove("/tmp/test_audit_ledger.jsonl")
