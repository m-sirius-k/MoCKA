"""
HG-M3 Phase 3: Component A4 - Failure Handling Protocols

Implement 5 failure pattern detection methods:
1. Evidence Missing
2. Conflict
3. Authority Missing
4. Validation Failure
5. Timestamp Conflict

All failures escalate to Human Gate.
Implement recovery procedure templates.

Status: DESIGN LAYER ONLY (detection and routing, no enforcement)
Environment: SANDBOX ONLY
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Literal
from enum import Enum


class FailurePattern(Enum):
    """5 failure patterns in Phase 3"""
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    CONFLICT = "CONFLICT"
    AUTHORITY_MISSING = "AUTHORITY_MISSING"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    TIMESTAMP_CONFLICT = "TIMESTAMP_CONFLICT"


class SeverityLevel(Enum):
    """Severity levels for failures"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FailureDetector:
    """Detect and classify failures"""

    @staticmethod
    def detect_evidence_missing(evidence_ids: List[str], available_evidence: List[str]) -> Optional[Dict]:
        """
        Failure 1: Evidence Missing

        Trigger: Referenced evidence does not exist

        Args:
            evidence_ids: Evidence IDs that should exist
            available_evidence: Evidence IDs that actually exist

        Returns:
            Failure record dict or None
        """
        missing = set(evidence_ids) - set(available_evidence)
        if missing:
            return {
                "pattern": FailurePattern.EVIDENCE_MISSING.value,
                "severity": SeverityLevel.HIGH.value,
                "missing_ids": list(missing),
                "detail": f"Evidence missing: {missing}"
            }
        return None

    @staticmethod
    def detect_conflict(decision_id: str, existing_decision: Optional[Dict]) -> Optional[Dict]:
        """
        Failure 2: Conflict

        Trigger: Decision already exists or conflicts with existing state

        Args:
            decision_id: Decision being created
            existing_decision: Existing decision data (if any)

        Returns:
            Failure record dict or None
        """
        if existing_decision:
            return {
                "pattern": FailurePattern.CONFLICT.value,
                "severity": SeverityLevel.CRITICAL.value,
                "conflict_with": decision_id,
                "detail": "Decision already exists or conflicts with existing state"
            }
        return None

    @staticmethod
    def detect_authority_missing(authority_id: str, authority_registry: Dict) -> Optional[Dict]:
        """
        Failure 3: Authority Missing

        Trigger: Referenced authority is not registered

        Args:
            authority_id: Authority ID to check
            authority_registry: Registry of registered authorities

        Returns:
            Failure record dict or None
        """
        if authority_id not in authority_registry:
            return {
                "pattern": FailurePattern.AUTHORITY_MISSING.value,
                "severity": SeverityLevel.HIGH.value,
                "authority_id": authority_id,
                "detail": f"Authority {authority_id} not found in registry"
            }
        return None

    @staticmethod
    def detect_validation_failure(check_results: Dict[int, Literal["PASS", "FAIL"]]) -> Optional[Dict]:
        """
        Failure 4: Validation Failure

        Trigger: One or more validation checks failed

        Args:
            check_results: Results from 6-check validation pipeline

        Returns:
            Failure record dict or None
        """
        failed_checks = [k for k, v in check_results.items() if v == "FAIL"]
        if failed_checks:
            return {
                "pattern": FailurePattern.VALIDATION_FAILURE.value,
                "severity": SeverityLevel.HIGH.value,
                "failed_checks": failed_checks,
                "detail": f"Validation failed on checks: {failed_checks}"
            }
        return None

    @staticmethod
    def detect_timestamp_conflict(timestamps: List[tuple[str, str]]) -> Optional[Dict]:
        """
        Failure 5: Timestamp Conflict

        Trigger: Evidence timestamps not in correct order

        Args:
            timestamps: List of (id, timestamp) tuples

        Returns:
            Failure record dict or None
        """
        if len(timestamps) < 2:
            return None

        sorted_ts = sorted(timestamps, key=lambda x: x[1])
        original_order = [x[0] for x in timestamps]
        sorted_order = [x[0] for x in sorted_ts]

        if original_order != sorted_order:
            return {
                "pattern": FailurePattern.TIMESTAMP_CONFLICT.value,
                "severity": SeverityLevel.MEDIUM.value,
                "original_order": original_order,
                "correct_order": sorted_order,
                "detail": "Evidence timestamps not in correct order"
            }
        return None


class FailureEscalation:
    """Route failures to Human Gate"""

    def __init__(self):
        self.escalations: List[Dict] = []

    def escalate_to_human_gate(self, failure: Dict, decision_id: str) -> Dict:
        """
        Escalate failure to Human Gate

        Args:
            failure: Failure record from detector
            decision_id: Associated decision ID

        Returns:
            Escalation record
        """
        escalation = {
            "escalation_id": f"ESC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "decision_id": decision_id,
            "failure_pattern": failure["pattern"],
            "severity": failure["severity"],
            "detail": failure["detail"],
            "status": "ESCALATED_TO_HUMAN_GATE",
            "human_gate_response": None,
            "recovery_action": None
        }

        self.escalations.append(escalation)
        return escalation

    def get_pending_escalations(self) -> List[Dict]:
        """Get all pending escalations"""
        return [e for e in self.escalations if e["status"] == "ESCALATED_TO_HUMAN_GATE"]

    def record_human_gate_decision(self, escalation_id: str, response: Literal["APPROVE", "REJECT", "CONDITIONAL"]) -> Dict:
        """
        Record Human Gate's decision on escalation

        Args:
            escalation_id: Escalation to respond to
            response: Human Gate's decision

        Returns:
            Updated escalation record
        """
        for esc in self.escalations:
            if esc["escalation_id"] == escalation_id:
                esc["human_gate_response"] = response
                if response == "APPROVE":
                    esc["status"] = "APPROVED_BY_HUMAN_GATE"
                elif response == "REJECT":
                    esc["status"] = "REJECTED_BY_HUMAN_GATE"
                else:
                    esc["status"] = "CONDITIONAL_HUMAN_GATE"
                return esc
        return {}

    def export_json(self) -> str:
        """Export escalations as JSON"""
        return json.dumps(self.escalations, indent=2, ensure_ascii=True)


class RecoveryProcedureTemplate:
    """Templates for recovery procedures"""

    PROCEDURES = {
        FailurePattern.EVIDENCE_MISSING.value: {
            "name": "Evidence Missing Recovery",
            "steps": [
                "1. Identify missing evidence IDs",
                "2. Check if evidence is available elsewhere",
                "3. If evidence found: update binding and re-run validation",
                "4. If evidence not found: escalate to Human Gate",
                "5. Await Human Gate decision",
                "6. If approved: mark evidence as optional or waive requirement",
                "7. If rejected: rollback and terminate decision"
            ],
            "estimated_time": "15-30 minutes"
        },
        FailurePattern.CONFLICT.value: {
            "name": "Conflict Resolution",
            "steps": [
                "1. Identify conflicting decision/resource",
                "2. Determine conflict type (duplicate, state conflict, etc.)",
                "3. Escalate to Human Gate with both versions",
                "4. Await Human Gate resolution decision",
                "5. If keep existing: terminate new decision",
                "6. If replace: archive old, activate new",
                "7. If merge: create merged decision"
            ],
            "estimated_time": "30-60 minutes"
        },
        FailurePattern.AUTHORITY_MISSING.value: {
            "name": "Authority Registration Recovery",
            "steps": [
                "1. Identify missing authority ID",
                "2. Check authority registry for similar entries",
                "3. Escalate to Human Gate with authority details",
                "4. Await Human Gate authorization",
                "5. If approved: register authority in sandbox",
                "6. If rejected: use alternative authority or terminate",
                "7. Re-run validation with registered authority"
            ],
            "estimated_time": "20-45 minutes"
        },
        FailurePattern.VALIDATION_FAILURE.value: {
            "name": "Validation Failure Recovery",
            "steps": [
                "1. Identify failed checks (from 1-6 pipeline)",
                "2. Analyze root cause of each failure",
                "3. If fixable in code: implement fix and re-run validation",
                "4. If unfixable: escalate to Human Gate",
                "5. If overridable: get Human Gate override approval",
                "6. If not overridable: rollback and terminate"
            ],
            "estimated_time": "30-90 minutes"
        },
        FailurePattern.TIMESTAMP_CONFLICT.value: {
            "name": "Timestamp Ordering Recovery",
            "steps": [
                "1. Identify out-of-order timestamps",
                "2. Check if timestamps are editable/correctable",
                "3. If fixable: correct timestamps to proper order",
                "4. If not fixable: escalate to Human Gate",
                "5. Await Human Gate guidance on data validity",
                "6. If approved: accept with audit note",
                "7. If rejected: remove conflicting evidence and re-validate"
            ],
            "estimated_time": "15-45 minutes"
        }
    }

    @staticmethod
    def get_procedure(failure_pattern: str) -> Dict:
        """Get recovery procedure for failure pattern"""
        return RecoveryProcedureTemplate.PROCEDURES.get(
            failure_pattern,
            {
                "name": "Unknown Failure Recovery",
                "steps": ["Escalate to Human Gate"],
                "estimated_time": "unknown"
            }
        )


# Example usage
if __name__ == "__main__":
    print("Failure Handling Protocols - 5 Patterns")
    print("=" * 60)

    detector = FailureDetector()
    escalation = FailureEscalation()

    # Test Failure 1: Evidence Missing
    print("\n1. Evidence Missing Detection:")
    failure = detector.detect_evidence_missing(
        ["EVD_001", "EVD_002", "EVD_003"],
        ["EVD_001", "EVD_002"]
    )
    if failure:
        print(f"  Detected: {failure}")
        esc = escalation.escalate_to_human_gate(failure, "DEC_001")
        print(f"  Escalation: {esc['escalation_id']}")

    # Test Failure 2: Conflict
    print("\n2. Conflict Detection:")
    failure = detector.detect_conflict("DEC_001", {"decision_id": "DEC_001"})
    if failure:
        print(f"  Detected: {failure}")
        esc = escalation.escalate_to_human_gate(failure, "DEC_001")
        print(f"  Escalation: {esc['escalation_id']}")

    # Test Failure 3: Authority Missing
    print("\n3. Authority Missing Detection:")
    failure = detector.detect_authority_missing("AUT_999", {"AUT_001": {}})
    if failure:
        print(f"  Detected: {failure}")
        esc = escalation.escalate_to_human_gate(failure, "DEC_001")
        print(f"  Escalation: {esc['escalation_id']}")

    # Test Failure 4: Validation Failure
    print("\n4. Validation Failure Detection:")
    failure = detector.detect_validation_failure({1: "PASS", 2: "FAIL", 3: "PASS"})
    if failure:
        print(f"  Detected: {failure}")
        esc = escalation.escalate_to_human_gate(failure, "DEC_001")
        print(f"  Escalation: {esc['escalation_id']}")

    # Test Failure 5: Timestamp Conflict
    print("\n5. Timestamp Conflict Detection:")
    failure = detector.detect_timestamp_conflict([
        ("EVD_001", "2026-09-18T08:00:00Z"),
        ("EVD_002", "2026-09-18T07:00:00Z")
    ])
    if failure:
        print(f"  Detected: {failure}")
        esc = escalation.escalate_to_human_gate(failure, "DEC_001")
        print(f"  Escalation: {esc['escalation_id']}")

    # Show recovery procedures
    print("\n" + "=" * 60)
    print("Recovery Procedures for Each Failure Pattern:")
    for pattern in FailurePattern:
        proc = RecoveryProcedureTemplate.get_procedure(pattern.value)
        print(f"\n{proc['name']}:")
        for step in proc['steps']:
            print(f"  {step}")

    # Export escalations
    print("\n" + "=" * 60)
    print("All Escalations:")
    print(escalation.export_json())
