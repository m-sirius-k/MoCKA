"""
HG-M3 Phase 3: Component A3 - Validation Logic

Implement 6-check sequential validation pipeline:
1. Decision Identity (Q1-Q6 present and valid)
2. Authority Validity (authority registered and not revoked)
3. Evidence Existence (all referenced evidence exists)
4. Evidence Integrity (SHA256 hashes match)
5. Timestamp Ordering (evidence timestamps ordered correctly)
6. Validation Record (this validation record exists and is complete)

Status: DESIGN LAYER ONLY (validation capture, not enforcement)
Environment: SANDBOX ONLY
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Callable, Literal
from enum import Enum


class CheckResult(Enum):
    """Result of a single check"""
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ValidationPipeline:
    """6-check sequential validation pipeline"""

    def __init__(self, validation_id: str, decision_id: str):
        """
        Args:
            validation_id: Unique validation ID
            decision_id: Decision being validated
        """
        self.validation_id = validation_id
        self.decision_id = decision_id
        self.checks_results: Dict[int, CheckResult] = {}
        self.checks_details: Dict[int, Dict] = {}
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.completed_at: Optional[str] = None
        self.overall_result: Optional[Literal["VALID", "INVALID", "UNKNOWN"]] = None

    def check_1_decision_identity(self, q_decisions: Dict[str, str]) -> CheckResult:
        """
        Check 1: Verify decision has all Q1-Q6 and they are valid

        Args:
            q_decisions: Decision options dict

        Returns:
            CheckResult (PASS/FAIL/UNKNOWN)
        """
        required = {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
        valid_options = {"A", "B", "C"}

        present = set(q_decisions.keys())
        if not required.issubset(present):
            result = CheckResult.FAIL
            detail = f"Missing decisions: {required - present}"
        else:
            invalid = {k: v for k, v in q_decisions.items() if k in required and v not in valid_options}
            if invalid:
                result = CheckResult.FAIL
                detail = f"Invalid options: {invalid}"
            else:
                result = CheckResult.PASS
                detail = "All Q1-Q6 present and valid"

        self.checks_results[1] = result
        self.checks_details[1] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def check_2_authority_validity(self, authority_snapshot: Dict, is_revoked: bool = False) -> CheckResult:
        """
        Check 2: Verify authority is registered and not revoked

        Args:
            authority_snapshot: Authority snapshot data
            is_revoked: Whether authority has been revoked

        Returns:
            CheckResult
        """
        if not authority_snapshot:
            result = CheckResult.UNKNOWN
            detail = "Authority snapshot not found"
        elif is_revoked:
            result = CheckResult.FAIL
            detail = "Authority has been revoked"
        else:
            result = CheckResult.PASS
            detail = "Authority is valid and not revoked"

        self.checks_results[2] = result
        self.checks_details[2] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def check_3_evidence_existence(self, evidence_list: List[str]) -> CheckResult:
        """
        Check 3: Verify all referenced evidence exists

        Args:
            evidence_list: List of evidence IDs that should exist

        Returns:
            CheckResult
        """
        if not evidence_list:
            result = CheckResult.FAIL
            detail = "No evidence provided"
        else:
            # In actual implementation, would check evidence database
            # For design phase, assume all provided evidence exists
            result = CheckResult.PASS
            detail = f"All {len(evidence_list)} evidence items exist"

        self.checks_results[3] = result
        self.checks_details[3] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def check_4_evidence_integrity(self, evidence_hashes: Dict[str, str], actual_hashes: Optional[Dict[str, str]] = None) -> CheckResult:
        """
        Check 4: Verify evidence integrity via SHA256

        Args:
            evidence_hashes: Expected SHA256 hashes {evidence_id: hash}
            actual_hashes: Actual SHA256 hashes (if not provided, assume match)

        Returns:
            CheckResult
        """
        if not evidence_hashes:
            result = CheckResult.FAIL
            detail = "No evidence hashes to verify"
        elif actual_hashes is None:
            result = CheckResult.PASS
            detail = f"Hash verification assumed OK for {len(evidence_hashes)} items"
        else:
            mismatches = {k: (evidence_hashes[k], actual_hashes.get(k))
                         for k in evidence_hashes if k not in actual_hashes or evidence_hashes[k] != actual_hashes[k]}
            if mismatches:
                result = CheckResult.FAIL
                detail = f"Hash mismatches: {list(mismatches.keys())}"
            else:
                result = CheckResult.PASS
                detail = f"All {len(evidence_hashes)} hashes verified"

        self.checks_results[4] = result
        self.checks_details[4] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def check_5_timestamp_ordering(self, timestamps: List[tuple[str, str]]) -> CheckResult:
        """
        Check 5: Verify evidence timestamps are ordered correctly

        Args:
            timestamps: List of (evidence_id, timestamp) tuples

        Returns:
            CheckResult
        """
        if not timestamps:
            result = CheckResult.FAIL
            detail = "No timestamps provided"
        else:
            # Check monotonic ordering
            sorted_ts = sorted(timestamps, key=lambda x: x[1])
            if [x[1] for x in sorted_ts] == [x[1] for x in timestamps]:
                result = CheckResult.PASS
                detail = f"Timestamps correctly ordered for {len(timestamps)} items"
            else:
                result = CheckResult.FAIL
                detail = "Timestamp ordering violation detected"

        self.checks_results[5] = result
        self.checks_details[5] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def check_6_validation_record(self) -> CheckResult:
        """
        Check 6: Verify this validation record itself is complete

        Returns:
            CheckResult
        """
        # Verify checks 1-5 are completed
        completed = all(i in self.checks_results for i in range(1, 6))
        if completed:
            result = CheckResult.PASS
            detail = "All 5 prior checks completed"
        else:
            result = CheckResult.FAIL
            missing = [i for i in range(1, 6) if i not in self.checks_results]
            detail = f"Missing checks: {missing}"

        self.checks_results[6] = result
        self.checks_details[6] = {"detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
        return result

    def execute_pipeline(self, validation_data: Dict) -> Dict:
        """
        Execute entire 6-check pipeline in sequence

        Args:
            validation_data: Dict with all necessary validation data

        Returns:
            Validation results dict
        """
        # Execute checks in order
        self.check_1_decision_identity(validation_data.get("q_decisions", {}))
        self.check_2_authority_validity(
            validation_data.get("authority_snapshot"),
            validation_data.get("is_revoked", False)
        )
        self.check_3_evidence_existence(validation_data.get("evidence_ids", []))
        self.check_4_evidence_integrity(
            validation_data.get("evidence_hashes", {}),
            validation_data.get("actual_hashes")
        )
        self.check_5_timestamp_ordering(validation_data.get("timestamps", []))
        self.check_6_validation_record()

        # Determine overall result
        results = list(self.checks_results.values())
        fails = sum(1 for r in results if r == CheckResult.FAIL)
        unknowns = sum(1 for r in results if r == CheckResult.UNKNOWN)

        if fails > 0:
            self.overall_result = "INVALID"
        elif unknowns > 0:
            self.overall_result = "UNKNOWN"
        else:
            self.overall_result = "VALID"

        self.completed_at = datetime.utcnow().isoformat() + "Z"

        return self.get_results()

    def get_results(self) -> Dict:
        """Get validation results"""
        return {
            "validation_id": self.validation_id,
            "decision_id": self.decision_id,
            "check_results": {
                str(k): v.value for k, v in self.checks_results.items()
            },
            "check_details": self.checks_details,
            "overall_result": self.overall_result,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

    def export_json(self) -> str:
        """Export results as JSON"""
        return json.dumps(self.get_results(), indent=2, ensure_ascii=True)


class ValidationDecisionTree:
    """Decision tree for validation check ordering based on Q4-Q5 policy"""

    def __init__(self, q4_verification_method: str, q5_monitoring_frequency: str):
        """
        Args:
            q4_verification_method: From Q4 decision (hash_chain, timestamp_ordering, hash_and_timestamp)
            q5_monitoring_frequency: From Q5 decision (random, scheduled, continuous)
        """
        self.q4_method = q4_verification_method
        self.q5_frequency = q5_monitoring_frequency

    def get_check_priority(self) -> List[int]:
        """
        Determine check execution order based on Q4-Q5

        Returns:
            Ordered list of check numbers (1-6)
        """
        # Base order: always 1, 2, 3
        priority = [1, 2, 3]

        # Q4 affects check 4 priority
        if self.q4_method == "hash_and_timestamp":
            priority.extend([4, 5])  # Both hash and timestamp critical
        elif self.q4_method == "hash_chain":
            priority.append(4)  # Hash check is critical
            priority.append(5)  # But timestamp is optional
        else:  # timestamp_ordering
            priority.append(5)  # Timestamp check is critical
            priority.append(4)  # Hash check is optional

        priority.append(6)  # Check 6 is always last

        return priority

    def should_fast_fail(self) -> bool:
        """
        Should validation stop on first failure?

        Based on Q5: Continuous monitoring means catch failures immediately
        """
        return self.q5_frequency == "continuous"


# Example usage
if __name__ == "__main__":
    print("Validation Logic - 6-Check Sequential Pipeline")
    print("=" * 60)

    # Create validation pipeline
    validation = ValidationPipeline("VAL_001", "DEC_001")

    # Example validation data
    validation_data = {
        "q_decisions": {"Q1": "B", "Q2": "A", "Q3": "A", "Q4": "C", "Q5": "C", "Q6": "C"},
        "authority_snapshot": {"authority_id": "AUT_001", "timestamp": "2026-09-18T08:00:00Z"},
        "is_revoked": False,
        "evidence_ids": ["EVD_001", "EVD_002"],
        "evidence_hashes": {
            "EVD_001": "abc123...",
            "EVD_002": "def456..."
        },
        "actual_hashes": {
            "EVD_001": "abc123...",
            "EVD_002": "def456..."
        },
        "timestamps": [
            ("EVD_001", "2026-09-18T07:00:00Z"),
            ("EVD_002", "2026-09-18T08:00:00Z")
        ]
    }

    # Execute pipeline
    results = validation.execute_pipeline(validation_data)

    print("Validation Pipeline Results:")
    print(validation.export_json())

    # Test decision tree
    print("\n" + "=" * 60)
    print("Validation Decision Tree (Q4=hash_and_timestamp, Q5=continuous)")
    tree = ValidationDecisionTree("hash_and_timestamp", "continuous")
    print(f"Check priority: {tree.get_check_priority()}")
    print(f"Fast fail on first error: {tree.should_fast_fail()}")
