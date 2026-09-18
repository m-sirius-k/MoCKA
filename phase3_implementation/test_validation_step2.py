#!/usr/bin/env python3
"""
HG-M3 Phase 3: STEP 2 - Validation Scenario Tests

8 validation scenarios testing real-world decision flows:
V01: Valid decision with all checks passing
V02: Decision with missing evidence
V03: Decision with conflict detected
V04: Authority validation failure (revoked)
V05: Timestamp ordering violation
V06: Hash integrity violation
V07: Decision with all checks failing
V08: Cascading failure recovery

Result: PASS/FAIL with detailed issue tracking
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from a1_design_interpretation import Q1Q6Configuration
from a2_binding_objects import (
    DecisionBindingObject, EvidenceBindingObject, AuthorityReferenceObject,
    ValidationRecordObject, BindingObjectRegistry, BindingState
)
from a3_validation_logic import ValidationPipeline, CheckResult
from a4_failure_handling import FailureDetector, FailureEscalation


class ValidationStep2:
    """STEP 2: Validation Scenario Tests"""

    def __init__(self):
        self.results = []
        self.total_pass = 0
        self.total_fail = 0

    def test_V01_valid_decision_all_checks_pass(self):
        """V01: Valid decision with all checks passing"""
        print("\nV01: Valid Decision - All Checks Pass")
        print("-" * 40)

        try:
            # Setup
            decision = DecisionBindingObject(
                "DEC_V01",
                {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "A", "Q5": "B", "Q6": "C"}
            )
            decision.verify()

            # Validate
            validation = ValidationPipeline("VAL_V01", "DEC_V01")
            results = validation.execute_pipeline({
                "q_decisions": decision.q_decisions,
                "authority_snapshot": {"authority_id": "AUT_001"},
                "is_revoked": False,
                "evidence_ids": ["EVD_001", "EVD_002"],
                "evidence_hashes": {"EVD_001": "hash1", "EVD_002": "hash2"},
                "actual_hashes": {"EVD_001": "hash1", "EVD_002": "hash2"},
                "timestamps": [
                    ("EVD_001", "2026-09-18T07:00:00Z"),
                    ("EVD_002", "2026-09-18T08:00:00Z")
                ]
            })

            passed = (
                results["overall_result"] == "VALID" and
                all(v == "PASS" for v in results["check_results"].values())
            )

            self.results.append({
                "scenario": "V01",
                "name": "Valid Decision - All Checks Pass",
                "result": "PASS" if passed else "FAIL",
                "checks_passed": sum(1 for v in results["check_results"].values() if v == "PASS"),
                "overall": results["overall_result"]
            })

            print(f"  Overall: {results['overall_result']}")
            print(f"  Checks: {sum(1 for v in results['check_results'].values() if v == 'PASS')}/6 PASS")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V01", "name": "Valid Decision", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V02_decision_with_missing_evidence(self):
        """V02: Decision with missing evidence"""
        print("\nV02: Missing Evidence Detection")
        print("-" * 40)

        try:
            detector = FailureDetector()
            escalation = FailureEscalation()

            # Detect missing evidence
            failure = detector.detect_evidence_missing(
                ["EVD_001", "EVD_002", "EVD_003"],
                ["EVD_001", "EVD_002"]
            )

            passed = failure is not None and failure["pattern"] == "EVIDENCE_MISSING"

            if passed:
                # Escalate
                esc = escalation.escalate_to_human_gate(failure, "DEC_V02")
                passed = esc["status"] == "ESCALATED_TO_HUMAN_GATE"

            self.results.append({
                "scenario": "V02",
                "name": "Missing Evidence Detection",
                "result": "PASS" if passed else "FAIL",
                "failure_pattern": failure["pattern"] if failure else None
            })

            print(f"  Failure detected: {failure['pattern'] if failure else 'None'}")
            print(f"  Escalation: {'ESCALATED' if passed else 'FAILED'}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V02", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V03_decision_with_conflict(self):
        """V03: Decision with conflict detected"""
        print("\nV03: Conflict Detection")
        print("-" * 40)

        try:
            detector = FailureDetector()

            # Detect conflict
            existing = {"decision_id": "DEC_V03", "state": "ACTIVE"}
            failure = detector.detect_conflict("DEC_V03", existing)

            passed = (
                failure is not None and
                failure["pattern"] == "CONFLICT" and
                failure["severity"] == "CRITICAL"
            )

            self.results.append({
                "scenario": "V03",
                "name": "Conflict Detection",
                "result": "PASS" if passed else "FAIL",
                "severity": failure["severity"] if failure else None
            })

            print(f"  Conflict detected: {failure['pattern'] if failure else 'None'}")
            print(f"  Severity: {failure['severity'] if failure else 'N/A'}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V03", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V04_authority_validation_failure(self):
        """V04: Authority validation failure (revoked)"""
        print("\nV04: Authority Revocation Detection")
        print("-" * 40)

        try:
            # Create authority with revocation
            authority = AuthorityReferenceObject(
                "AUT_V04",
                "DEC_V04",
                "2026-09-18T08:00:00Z"
            )
            authority.check_revocation(True)

            passed = (
                authority.state == BindingState.INVALID and
                authority.is_revoked == True
            )

            self.results.append({
                "scenario": "V04",
                "name": "Authority Revocation Detection",
                "result": "PASS" if passed else "FAIL",
                "state": authority.state.value,
                "revoked": authority.is_revoked
            })

            print(f"  Authority state: {authority.state.value}")
            print(f"  Revoked: {authority.is_revoked}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V04", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V05_timestamp_ordering_violation(self):
        """V05: Timestamp ordering violation"""
        print("\nV05: Timestamp Ordering Violation")
        print("-" * 40)

        try:
            detector = FailureDetector()

            # Detect out-of-order timestamps
            failure = detector.detect_timestamp_conflict([
                ("EVD_001", "2026-09-18T08:00:00Z"),
                ("EVD_002", "2026-09-18T07:00:00Z"),
                ("EVD_003", "2026-09-18T06:00:00Z")
            ])

            passed = (
                failure is not None and
                failure["pattern"] == "TIMESTAMP_CONFLICT"
            )

            self.results.append({
                "scenario": "V05",
                "name": "Timestamp Ordering Violation",
                "result": "PASS" if passed else "FAIL",
                "pattern": failure["pattern"] if failure else None
            })

            print(f"  Violation detected: {failure['pattern'] if failure else 'None'}")
            if failure:
                print(f"  Original order: {failure.get('original_order')}")
                print(f"  Correct order: {failure.get('correct_order')}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V05", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V06_hash_integrity_violation(self):
        """V06: Hash integrity violation"""
        print("\nV06: Hash Integrity Violation")
        print("-" * 40)

        try:
            validation = ValidationPipeline("VAL_V06", "DEC_V06")

            # Check with hash mismatch
            result = validation.check_4_evidence_integrity(
                {"EVD_001": "expected_hash", "EVD_002": "expected_hash2"},
                {"EVD_001": "different_hash", "EVD_002": "expected_hash2"}
            )

            passed = result == CheckResult.FAIL

            self.results.append({
                "scenario": "V06",
                "name": "Hash Integrity Violation",
                "result": "PASS" if passed else "FAIL",
                "check_result": result.value
            })

            print(f"  Check result: {result.value}")
            print(f"  Hash mismatch detected: {passed}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V06", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V07_all_checks_failing(self):
        """V07: Decision with all checks failing"""
        print("\nV07: All Checks Failing")
        print("-" * 40)

        try:
            validation = ValidationPipeline("VAL_V07", "DEC_V07")

            results = validation.execute_pipeline({
                "q_decisions": {"Q1": "X"},  # Invalid
                "authority_snapshot": None,  # Missing
                "is_revoked": True,  # Revoked
                "evidence_ids": [],  # Empty
                "evidence_hashes": {},  # Empty
                "actual_hashes": {"EVD_001": "hash"},  # Mismatch
                "timestamps": []  # Empty
            })

            passed = results["overall_result"] == "INVALID"
            fails = sum(1 for v in results["check_results"].values() if v == "FAIL")

            self.results.append({
                "scenario": "V07",
                "name": "All Checks Failing",
                "result": "PASS" if passed else "FAIL",
                "overall": results["overall_result"],
                "failed_checks": fails
            })

            print(f"  Overall: {results['overall_result']}")
            print(f"  Failed checks: {fails}")

            if passed:
                self.total_pass += 1
            else:
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V07", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_V08_cascading_failure_recovery(self):
        """V08: Cascading failure recovery"""
        print("\nV08: Cascading Failure Recovery")
        print("-" * 40)

        try:
            detector = FailureDetector()
            escalation = FailureEscalation()

            # Detect first failure
            failure1 = detector.detect_evidence_missing(
                ["EVD_001", "EVD_002"],
                []
            )

            if failure1:
                esc1 = escalation.escalate_to_human_gate(failure1, "DEC_V08")
                esc_id = esc1["escalation_id"]

                # Simulate Human Gate approval
                updated = escalation.record_human_gate_decision(esc_id, "APPROVE")

                # Attempt second validation with corrected state
                validation = ValidationPipeline("VAL_V08", "DEC_V08")
                results = validation.execute_pipeline({
                    "q_decisions": {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "A", "Q5": "B", "Q6": "C"},
                    "authority_snapshot": {"authority_id": "AUT_001"},
                    "is_revoked": False,
                    "evidence_ids": ["EVD_001", "EVD_002"],
                    "evidence_hashes": {"EVD_001": "h1", "EVD_002": "h2"},
                    "actual_hashes": {"EVD_001": "h1", "EVD_002": "h2"},
                    "timestamps": [
                        ("EVD_001", "2026-09-18T07:00:00Z"),
                        ("EVD_002", "2026-09-18T08:00:00Z")
                    ]
                })

                passed = (
                    updated["status"] == "APPROVED_BY_HUMAN_GATE" and
                    results["overall_result"] == "VALID"
                )

                self.results.append({
                    "scenario": "V08",
                    "name": "Cascading Failure Recovery",
                    "result": "PASS" if passed else "FAIL",
                    "escalation_status": updated["status"],
                    "recovery_result": results["overall_result"]
                })

                print(f"  Initial failure: {failure1['pattern']}")
                print(f"  Escalation status: {updated['status']}")
                print(f"  Recovery result: {results['overall_result']}")

                if passed:
                    self.total_pass += 1
                else:
                    self.total_fail += 1
            else:
                self.results.append({"scenario": "V08", "result": "FAIL"})
                self.total_fail += 1

        except Exception as e:
            self.results.append({"scenario": "V08", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def run_all_scenarios(self):
        """Execute all 8 validation scenarios"""
        print("\n" + "=" * 60)
        print("HG-M3 PHASE 3 - STEP 2: VALIDATION SCENARIO TESTS")
        print("=" * 60)

        self.test_V01_valid_decision_all_checks_pass()
        self.test_V02_decision_with_missing_evidence()
        self.test_V03_decision_with_conflict()
        self.test_V04_authority_validation_failure()
        self.test_V05_timestamp_ordering_violation()
        self.test_V06_hash_integrity_violation()
        self.test_V07_all_checks_failing()
        self.test_V08_cascading_failure_recovery()

        # Summary
        print("\n" + "=" * 60)
        print("SCENARIO TEST SUMMARY")
        print("=" * 60)

        for result in self.results:
            print(f"{result['scenario']}: {result['result']} - {result.get('name', 'Unknown')}")

        print(f"\nTotal: {self.total_pass} PASS / {self.total_fail} FAIL")

        overall = "PASS" if self.total_fail == 0 else "FAIL"
        print(f"\nSTEP 2 OVERALL RESULT: {overall}")

        return {
            "step": "STEP_2_SCENARIOS",
            "status": overall,
            "scenarios": self.results,
            "total_pass": self.total_pass,
            "total_fail": self.total_fail,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
        }


if __name__ == "__main__":
    validator = ValidationStep2()
    results = validator.run_all_scenarios()

    output_file = Path(__file__).parent / "step2_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=True)
    print(f"\nResults saved to: {output_file}")
