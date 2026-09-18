"""
HG-M3 Phase 3: Component A2 - Binding Objects

Implement 5 binding object types:
1. Decision binding object
2. Evidence binding object
3. Authority Reference object
4. Validation Record object
5. Audit Reference object

All with state transition logic: VALID/INVALID/UNKNOWN/NOT_VERIFIED

Status: DESIGN LAYER ONLY (schemas and state logic, no enforcement)
Environment: SANDBOX ONLY
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Literal
from enum import Enum


class BindingState(Enum):
    """Valid binding states"""
    VALID = "VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"
    NOT_VERIFIED = "NOT_VERIFIED"


class DecisionBindingObject:
    """Decision binding object - binds decision to Q1-Q6 options"""

    def __init__(self, decision_id: str, q_decisions: Dict[str, str]):
        """
        Args:
            decision_id: Unique decision identifier
            q_decisions: Dict {Q1: A/B/C, Q2: A/B/C, ..., Q6: A/B/C}
        """
        self.decision_id = decision_id
        self.q_decisions = q_decisions
        self.state = BindingState.NOT_VERIFIED
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.verified_at: Optional[str] = None

    def verify(self) -> None:
        """Verify decision binding (transition to VALID)"""
        # Validate Q1-Q6 are all present and valid (A/B/C)
        required_questions = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
        if all(q in self.q_decisions and self.q_decisions[q] in ["A", "B", "C"] for q in required_questions):
            self.state = BindingState.VALID
            self.verified_at = datetime.utcnow().isoformat() + "Z"
        else:
            self.state = BindingState.INVALID

    def invalidate(self) -> None:
        """Invalidate binding"""
        self.state = BindingState.INVALID

    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "q_decisions": self.q_decisions,
            "state": self.state.value,
            "created_at": self.created_at,
            "verified_at": self.verified_at
        }


class EvidenceBindingObject:
    """Evidence binding object - binds evidence to decision"""

    def __init__(self, evidence_id: str, decision_id: str, evidence_type: str, sha256_hash: str):
        """
        Args:
            evidence_id: Unique evidence identifier
            decision_id: Linked decision ID
            evidence_type: Type of evidence (synthetic_evidence, etc.)
            sha256_hash: SHA256 hash of evidence
        """
        self.evidence_id = evidence_id
        self.decision_id = decision_id
        self.evidence_type = evidence_type
        self.sha256_hash = sha256_hash
        self.state = BindingState.NOT_VERIFIED
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.hash_verified_at: Optional[str] = None

    def verify_hash(self, actual_hash: str) -> None:
        """Verify evidence integrity"""
        if actual_hash == self.sha256_hash:
            self.state = BindingState.VALID
            self.hash_verified_at = datetime.utcnow().isoformat() + "Z"
        else:
            self.state = BindingState.INVALID

    def mark_unknown(self) -> None:
        """Mark evidence as unknown (access failed)"""
        self.state = BindingState.UNKNOWN

    def to_dict(self) -> Dict:
        return {
            "evidence_id": self.evidence_id,
            "decision_id": self.decision_id,
            "evidence_type": self.evidence_type,
            "sha256_hash": self.sha256_hash,
            "state": self.state.value,
            "created_at": self.created_at,
            "hash_verified_at": self.hash_verified_at
        }


class AuthorityReferenceObject:
    """Authority Reference object - tracks authority snapshots"""

    def __init__(self, authority_id: str, decision_id: str, snapshot_timestamp: str):
        """
        Args:
            authority_id: Unique authority identifier
            decision_id: Linked decision ID
            snapshot_timestamp: Authority snapshot timestamp (ISO 8601)
        """
        self.authority_id = authority_id
        self.decision_id = decision_id
        self.snapshot_timestamp = snapshot_timestamp
        self.state = BindingState.NOT_VERIFIED
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.revocation_checked_at: Optional[str] = None
        self.is_revoked = False

    def check_revocation(self, revoked: bool) -> None:
        """Check if authority has been revoked"""
        self.revocation_checked_at = datetime.utcnow().isoformat() + "Z"
        if revoked:
            self.state = BindingState.INVALID
            self.is_revoked = True
        else:
            self.state = BindingState.VALID
            self.is_revoked = False

    def mark_expired(self) -> None:
        """Mark authority snapshot as expired"""
        self.state = BindingState.INVALID

    def to_dict(self) -> Dict:
        return {
            "authority_id": self.authority_id,
            "decision_id": self.decision_id,
            "snapshot_timestamp": self.snapshot_timestamp,
            "state": self.state.value,
            "created_at": self.created_at,
            "revocation_checked_at": self.revocation_checked_at,
            "is_revoked": self.is_revoked
        }


class ValidationRecordObject:
    """Validation Record object - captures all 6 validation checks"""

    def __init__(self, record_id: str, decision_id: str):
        """
        Args:
            record_id: Unique validation record ID
            decision_id: Linked decision ID
        """
        self.record_id = record_id
        self.decision_id = decision_id
        self.checks: Dict[str, Literal["PASS", "FAIL", "UNKNOWN"]] = {
            "check_1_decision_identity": "UNKNOWN",
            "check_2_authority_validity": "UNKNOWN",
            "check_3_evidence_existence": "UNKNOWN",
            "check_4_evidence_integrity": "UNKNOWN",
            "check_5_timestamp_ordering": "UNKNOWN",
            "check_6_validation_record": "UNKNOWN"
        }
        self.state = BindingState.NOT_VERIFIED
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.completed_at: Optional[str] = None

    def record_check_result(self, check_number: int, result: Literal["PASS", "FAIL", "UNKNOWN"]) -> None:
        """Record result of individual check"""
        check_name = f"check_{check_number}_"
        for key in self.checks:
            if key.startswith(check_name):
                self.checks[key] = result
                break

    def finalize(self) -> None:
        """Finalize validation record"""
        all_passed = all(v == "PASS" for v in self.checks.values())
        any_failed = any(v == "FAIL" for v in self.checks.values())

        if all_passed:
            self.state = BindingState.VALID
        elif any_failed:
            self.state = BindingState.INVALID
        else:
            self.state = BindingState.UNKNOWN

        self.completed_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "decision_id": self.decision_id,
            "checks": self.checks,
            "state": self.state.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


class AuditReferenceObject:
    """Audit Reference object - links to audit trail entries"""

    def __init__(self, audit_id: str, decision_id: str, retention_policy: str):
        """
        Args:
            audit_id: Unique audit trail ID
            decision_id: Linked decision ID
            retention_policy: Retention period (e.g., "5_year_sandbox_only")
        """
        self.audit_id = audit_id
        self.decision_id = decision_id
        self.retention_policy = retention_policy
        self.state = BindingState.VALID  # Audit refs are valid by default
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.searchable = True
        self.tamper_detected = False

    def detect_tampering(self) -> None:
        """Mark audit reference as tampered"""
        self.state = BindingState.INVALID
        self.tamper_detected = True

    def to_dict(self) -> Dict:
        return {
            "audit_id": self.audit_id,
            "decision_id": self.decision_id,
            "retention_policy": self.retention_policy,
            "state": self.state.value,
            "created_at": self.created_at,
            "searchable": self.searchable,
            "tamper_detected": self.tamper_detected
        }


class BindingObjectRegistry:
    """Registry for managing all binding objects"""

    def __init__(self):
        self.decisions: Dict[str, DecisionBindingObject] = {}
        self.evidence: Dict[str, EvidenceBindingObject] = {}
        self.authorities: Dict[str, AuthorityReferenceObject] = {}
        self.validations: Dict[str, ValidationRecordObject] = {}
        self.audits: Dict[str, AuditReferenceObject] = {}

    def add_decision_binding(self, obj: DecisionBindingObject) -> None:
        self.decisions[obj.decision_id] = obj

    def add_evidence_binding(self, obj: EvidenceBindingObject) -> None:
        self.evidence[obj.evidence_id] = obj

    def add_authority_reference(self, obj: AuthorityReferenceObject) -> None:
        self.authorities[obj.authority_id] = obj

    def add_validation_record(self, obj: ValidationRecordObject) -> None:
        self.validations[obj.record_id] = obj

    def add_audit_reference(self, obj: AuditReferenceObject) -> None:
        self.audits[obj.audit_id] = obj

    def get_binding_summary(self) -> Dict:
        """Get summary of all binding objects"""
        return {
            "decision_bindings": len(self.decisions),
            "evidence_bindings": len(self.evidence),
            "authority_references": len(self.authorities),
            "validation_records": len(self.validations),
            "audit_references": len(self.audits),
            "total_bindings": (len(self.decisions) + len(self.evidence) +
                             len(self.authorities) + len(self.validations) +
                             len(self.audits))
        }

    def export_json(self) -> str:
        """Export all binding objects as JSON"""
        data = {
            "decisions": {k: v.to_dict() for k, v in self.decisions.items()},
            "evidence": {k: v.to_dict() for k, v in self.evidence.items()},
            "authorities": {k: v.to_dict() for k, v in self.authorities.items()},
            "validations": {k: v.to_dict() for k, v in self.validations.items()},
            "audits": {k: v.to_dict() for k, v in self.audits.items()}
        }
        return json.dumps(data, indent=2, ensure_ascii=True)


# Example usage
if __name__ == "__main__":
    print("Binding Objects - Schema and State Logic")
    print("=" * 60)

    registry = BindingObjectRegistry()

    # Create example decision binding
    decision = DecisionBindingObject(
        "DEC_001",
        {"Q1": "B", "Q2": "A", "Q3": "A", "Q4": "C", "Q5": "C", "Q6": "C"}
    )
    decision.verify()
    registry.add_decision_binding(decision)

    # Create example evidence binding
    evidence = EvidenceBindingObject(
        "EVD_001",
        "DEC_001",
        "synthetic_evidence",
        "abc123def456..."
    )
    evidence.verify_hash("abc123def456...")
    registry.add_evidence_binding(evidence)

    # Create example authority reference
    authority = AuthorityReferenceObject(
        "AUT_001",
        "DEC_001",
        "2026-09-18T08:00:00Z"
    )
    authority.check_revocation(False)
    registry.add_authority_reference(authority)

    # Create example validation record
    validation = ValidationRecordObject("VAL_001", "DEC_001")
    validation.record_check_result(1, "PASS")
    validation.record_check_result(2, "PASS")
    validation.record_check_result(3, "PASS")
    validation.record_check_result(4, "PASS")
    validation.record_check_result(5, "PASS")
    validation.record_check_result(6, "PASS")
    validation.finalize()
    registry.add_validation_record(validation)

    # Create example audit reference
    audit = AuditReferenceObject("AUD_001", "DEC_001", "5_year_sandbox_only")
    registry.add_audit_reference(audit)

    print("Registry Summary:")
    print(json.dumps(registry.get_binding_summary(), indent=2, ensure_ascii=True))

    print("\nAll Binding Objects:")
    print(registry.export_json())
