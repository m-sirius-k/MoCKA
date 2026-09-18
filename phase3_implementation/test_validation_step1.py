#!/usr/bin/env python3
"""
HG-M3 Phase 3: STEP 1 - Controlled Implementation Validation

Validates 5 components (A1-A5) against design specifications:
1. A1 Design Interpretation (Q1-Q6 configuration mapping)
2. A2 Binding Objects (state transitions)
3. A3 Validation Logic (6-check pipeline)
4. A4 Failure Handling (5 failure patterns)
5. A5 Audit Trail (immutability and hash-chain)

Result: PASS/FAIL with detailed issue tracking
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from a1_design_interpretation import Q1Q6Configuration, PolicyValidator
from a2_binding_objects import (
    DecisionBindingObject, EvidenceBindingObject, AuthorityReferenceObject,
    ValidationRecordObject, AuditReferenceObject, BindingObjectRegistry, BindingState
)
from a3_validation_logic import ValidationPipeline, CheckResult
from a4_failure_handling import FailureDetector, FailureEscalation, FailurePattern
from a5_audit_trail import AuditTrailManager


class ValidationStep1:
    """STEP 1: Controlled Implementation Validation"""

    def __init__(self):
        self.results = {
            "A1": {"status": None, "tests": []},
            "A2": {"status": None, "tests": []},
            "A3": {"status": None, "tests": []},
            "A4": {"status": None, "tests": []},
            "A5": {"status": None, "tests": []}
        }
        self.total_pass = 0
        self.total_fail = 0

    def test_A1_design_interpretation(self):
        """Test A1: Design Interpretation - Q1-Q6 Configuration Mapping"""
        print("\nSTEP 1.A1: Testing Design Interpretation (Q1-Q6 Configuration)")
        print("=" * 60)

        test_decisions = {
            "Q1": "B",
            "Q2": "A",
            "Q3": "A",
            "Q4": "C",
            "Q5": "C",
            "Q6": "C"
        }

        try:
            # Test 1: Create configuration
            config = Q1Q6Configuration(test_decisions)
            test1 = {"name": "Q1Q6Configuration creation", "result": "PASS"}

            # Test 2: Verify all Q1-Q6 mappings
            mappings = {
                "Q1": config.get_evidence_binding_check_type(),
                "Q2": config.get_authority_enforcement_rule(),
                "Q3": config.get_escalation_rule(),
                "Q4": config.get_verification_method(),
                "Q5": config.get_monitoring_frequency(),
                "Q6": config.get_recovery_type()
            }

            expected = {
                "Q1": "continuous_binding",
                "Q2": "pre_check_only",
                "Q3": "all_failures_to_hg",
                "Q4": "hash_and_timestamp",
                "Q5": "continuous",
                "Q6": "auto_with_audit"
            }

            all_match = all(mappings[k] == expected[k] for k in expected)
            test2 = {"name": "Q1-Q6 mapping verification", "result": "PASS" if all_match else "FAIL"}
            if not all_match:
                test2["detail"] = f"Mismatch: {mappings}"

            # Test 3: Policy validator consistency check
            policy = config.export_policy()
            issues = PolicyValidator.validate_consistency(policy)
            test3 = {"name": "Policy consistency validation", "result": "PASS" if not issues else "FAIL"}
            if issues:
                test3["detail"] = issues

            # Test 4: Export to JSON
            json_output = config.export_json()
            json_valid = json.loads(json_output) is not None
            test4 = {"name": "JSON export", "result": "PASS" if json_valid else "FAIL"}

            self.results["A1"]["tests"] = [test1, test2, test3, test4]
            self.results["A1"]["status"] = "PASS" if all(t["result"] == "PASS" for t in [test1, test2, test3, test4]) else "FAIL"

            for test in [test1, test2, test3, test4]:
                print(f"  {test['name']}: {test['result']}")
                if "detail" in test:
                    print(f"    -> {test['detail']}")

                if test["result"] == "PASS":
                    self.total_pass += 1
                else:
                    self.total_fail += 1

        except Exception as e:
            self.results["A1"]["status"] = "FAIL"
            self.results["A1"]["tests"].append({"name": "Exception", "result": "FAIL", "error": str(e)})
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_A2_binding_objects(self):
        """Test A2: Binding Objects - State Transitions"""
        print("\nSTEP 1.A2: Testing Binding Objects (State Transitions)")
        print("=" * 60)

        try:
            # Test 1: DecisionBindingObject
            decision = DecisionBindingObject(
                "DEC_TEST_001",
                {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "A", "Q5": "B", "Q6": "C"}
            )
            decision.verify()
            test1 = {"name": "DecisionBindingObject verification", "result": "PASS" if decision.state == BindingState.VALID else "FAIL"}

            # Test 2: EvidenceBindingObject
            evidence = EvidenceBindingObject(
                "EVD_TEST_001",
                "DEC_TEST_001",
                "test_evidence",
                "abc123def456"
            )
            evidence.verify_hash("abc123def456")
            test2 = {"name": "EvidenceBindingObject hash verification", "result": "PASS" if evidence.state == BindingState.VALID else "FAIL"}

            # Test 3: EvidenceBindingObject hash mismatch
            evidence_bad = EvidenceBindingObject(
                "EVD_TEST_002",
                "DEC_TEST_001",
                "test_evidence",
                "abc123"
            )
            evidence_bad.verify_hash("different_hash")
            test3 = {"name": "EvidenceBindingObject hash mismatch detection", "result": "PASS" if evidence_bad.state == BindingState.INVALID else "FAIL"}

            # Test 4: AuthorityReferenceObject
            authority = AuthorityReferenceObject(
                "AUT_TEST_001",
                "DEC_TEST_001",
                "2026-09-18T08:00:00Z"
            )
            authority.check_revocation(False)
            test4 = {"name": "AuthorityReferenceObject revocation check", "result": "PASS" if authority.state == BindingState.VALID else "FAIL"}

            # Test 5: ValidationRecordObject
            validation = ValidationRecordObject("VAL_TEST_001", "DEC_TEST_001")
            validation.record_check_result(1, "PASS")
            validation.record_check_result(2, "PASS")
            validation.record_check_result(3, "PASS")
            validation.record_check_result(4, "PASS")
            validation.record_check_result(5, "PASS")
            validation.record_check_result(6, "PASS")
            validation.finalize()
            test5 = {"name": "ValidationRecordObject finalization", "result": "PASS" if validation.state == BindingState.VALID else "FAIL"}

            # Test 6: AuditReferenceObject
            audit = AuditReferenceObject("AUD_TEST_001", "DEC_TEST_001", "5_year_sandbox")
            test6 = {"name": "AuditReferenceObject creation", "result": "PASS" if audit.state == BindingState.VALID else "FAIL"}

            # Test 7: BindingObjectRegistry
            registry = BindingObjectRegistry()
            registry.add_decision_binding(decision)
            registry.add_evidence_binding(evidence)
            registry.add_authority_reference(authority)
            registry.add_validation_record(validation)
            registry.add_audit_reference(audit)
            summary = registry.get_binding_summary()
            test7 = {"name": "BindingObjectRegistry management", "result": "PASS" if summary["total_bindings"] == 5 else "FAIL"}

            self.results["A2"]["tests"] = [test1, test2, test3, test4, test5, test6, test7]
            self.results["A2"]["status"] = "PASS" if all(t["result"] == "PASS" for t in [test1, test2, test3, test4, test5, test6, test7]) else "FAIL"

            for test in [test1, test2, test3, test4, test5, test6, test7]:
                print(f"  {test['name']}: {test['result']}")
                if test["result"] == "PASS":
                    self.total_pass += 1
                else:
                    self.total_fail += 1

        except Exception as e:
            self.results["A2"]["status"] = "FAIL"
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_A3_validation_logic(self):
        """Test A3: Validation Logic - 6-Check Pipeline"""
        print("\nSTEP 1.A3: Testing Validation Logic (6-Check Pipeline)")
        print("=" * 60)

        try:
            validation = ValidationPipeline("VAL_STEP1_001", "DEC_STEP1_001")

            # Test 1: Check 1 - Decision Identity
            result1 = validation.check_1_decision_identity(
                {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "A", "Q5": "B", "Q6": "C"}
            )
            test1 = {"name": "Check 1 - Decision Identity", "result": "PASS" if result1 == CheckResult.PASS else "FAIL"}

            # Test 2: Check 1 with missing Q
            validation2 = ValidationPipeline("VAL_STEP1_002", "DEC_STEP1_002")
            result_bad = validation2.check_1_decision_identity({"Q1": "A"})
            test2 = {"name": "Check 1 - Missing decisions detection", "result": "PASS" if result_bad == CheckResult.FAIL else "FAIL"}

            # Test 3: Check 2 - Authority Validity
            result2 = validation.check_2_authority_validity({"authority_id": "AUT_001"}, False)
            test3 = {"name": "Check 2 - Authority Validity", "result": "PASS" if result2 == CheckResult.PASS else "FAIL"}

            # Test 4: Check 3 - Evidence Existence
            result3 = validation.check_3_evidence_existence(["EVD_001", "EVD_002"])
            test4 = {"name": "Check 3 - Evidence Existence", "result": "PASS" if result3 == CheckResult.PASS else "FAIL"}

            # Test 5: Check 4 - Evidence Integrity
            result4 = validation.check_4_evidence_integrity(
                {"EVD_001": "hash1", "EVD_002": "hash2"},
                {"EVD_001": "hash1", "EVD_002": "hash2"}
            )
            test5 = {"name": "Check 4 - Evidence Integrity", "result": "PASS" if result4 == CheckResult.PASS else "FAIL"}

            # Test 6: Check 5 - Timestamp Ordering
            result5 = validation.check_5_timestamp_ordering([
                ("EVD_001", "2026-09-18T07:00:00Z"),
                ("EVD_002", "2026-09-18T08:00:00Z")
            ])
            test6 = {"name": "Check 5 - Timestamp Ordering", "result": "PASS" if result5 == CheckResult.PASS else "FAIL"}

            # Test 7: Check 6 - Validation Record
            result6 = validation.check_6_validation_record()
            test7 = {"name": "Check 6 - Validation Record", "result": "PASS" if result6 == CheckResult.PASS else "FAIL"}

            # Test 8: Full pipeline execution
            validation3 = ValidationPipeline("VAL_STEP1_003", "DEC_STEP1_003")
            results = validation3.execute_pipeline({
                "q_decisions": {"Q1": "A", "Q2": "B", "Q3": "C", "Q4": "A", "Q5": "B", "Q6": "C"},
                "authority_snapshot": {"authority_id": "AUT_001"},
                "is_revoked": False,
                "evidence_ids": ["EVD_001"],
                "evidence_hashes": {"EVD_001": "hash1"},
                "actual_hashes": {"EVD_001": "hash1"},
                "timestamps": [("EVD_001", "2026-09-18T08:00:00Z")]
            })
            test8 = {"name": "Full pipeline execution", "result": "PASS" if results["overall_result"] == "VALID" else "FAIL"}

            self.results["A3"]["tests"] = [test1, test2, test3, test4, test5, test6, test7, test8]
            self.results["A3"]["status"] = "PASS" if all(t["result"] == "PASS" for t in [test1, test2, test3, test4, test5, test6, test7, test8]) else "FAIL"

            for test in [test1, test2, test3, test4, test5, test6, test7, test8]:
                print(f"  {test['name']}: {test['result']}")
                if test["result"] == "PASS":
                    self.total_pass += 1
                else:
                    self.total_fail += 1

        except Exception as e:
            self.results["A3"]["status"] = "FAIL"
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_A4_failure_handling(self):
        """Test A4: Failure Handling - 5 Failure Patterns"""
        print("\nSTEP 1.A4: Testing Failure Handling (5 Patterns)")
        print("=" * 60)

        try:
            detector = FailureDetector()
            escalation = FailureEscalation()

            # Test 1: Detect Evidence Missing
            failure1 = detector.detect_evidence_missing(
                ["EVD_001", "EVD_002", "EVD_003"],
                ["EVD_001", "EVD_002"]
            )
            test1 = {"name": "Failure 1 - Evidence Missing detection", "result": "PASS" if failure1 is not None else "FAIL"}

            # Test 2: Detect Conflict
            failure2 = detector.detect_conflict("DEC_001", {"decision_id": "DEC_001"})
            test2 = {"name": "Failure 2 - Conflict detection", "result": "PASS" if failure2 is not None else "FAIL"}

            # Test 3: Detect Authority Missing
            failure3 = detector.detect_authority_missing("AUT_999", {"AUT_001": {}})
            test3 = {"name": "Failure 3 - Authority Missing detection", "result": "PASS" if failure3 is not None else "FAIL"}

            # Test 4: Detect Validation Failure
            failure4 = detector.detect_validation_failure({1: "PASS", 2: "FAIL", 3: "PASS"})
            test4 = {"name": "Failure 4 - Validation Failure detection", "result": "PASS" if failure4 is not None else "FAIL"}

            # Test 5: Detect Timestamp Conflict
            failure5 = detector.detect_timestamp_conflict([
                ("EVD_001", "2026-09-18T08:00:00Z"),
                ("EVD_002", "2026-09-18T07:00:00Z")
            ])
            test5 = {"name": "Failure 5 - Timestamp Conflict detection", "result": "PASS" if failure5 is not None else "FAIL"}

            # Test 6: Escalation to Human Gate
            if failure1:
                esc = escalation.escalate_to_human_gate(failure1, "DEC_001")
                test6 = {"name": "Escalation to Human Gate", "result": "PASS" if esc["status"] == "ESCALATED_TO_HUMAN_GATE" else "FAIL"}
            else:
                test6 = {"name": "Escalation to Human Gate", "result": "FAIL"}

            # Test 7: Record Human Gate Decision
            if failure1:
                esc = escalation.escalate_to_human_gate(failure1, "DEC_001")
                esc_id = esc["escalation_id"]
                updated = escalation.record_human_gate_decision(esc_id, "APPROVE")
                test7 = {"name": "Record Human Gate Decision", "result": "PASS" if updated["status"] == "APPROVED_BY_HUMAN_GATE" else "FAIL"}
            else:
                test7 = {"name": "Record Human Gate Decision", "result": "FAIL"}

            self.results["A4"]["tests"] = [test1, test2, test3, test4, test5, test6, test7]
            self.results["A4"]["status"] = "PASS" if all(t["result"] == "PASS" for t in [test1, test2, test3, test4, test5, test6, test7]) else "FAIL"

            for test in [test1, test2, test3, test4, test5, test6, test7]:
                print(f"  {test['name']}: {test['result']}")
                if test["result"] == "PASS":
                    self.total_pass += 1
                else:
                    self.total_fail += 1

        except Exception as e:
            self.results["A4"]["status"] = "FAIL"
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def test_A5_audit_trail(self):
        """Test A5: Audit Trail - Immutability and Hash-Chain"""
        print("\nSTEP 1.A5: Testing Audit Trail (Immutability & Hash-Chain)")
        print("=" * 60)

        try:
            import tempfile
            import os

            # Use temp file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
                ledger_file = f.name

            try:
                manager = AuditTrailManager(ledger_file)

                # Test 1: Log decision binding test
                entry1 = manager.log_decision_binding_test(
                    "DEC_001",
                    {"Q1": "B", "Q2": "A", "Q3": "A", "Q4": "C", "Q5": "C", "Q6": "C"},
                    "VALID"
                )
                test1 = {"name": "Log decision binding test", "result": "PASS" if entry1 is not None else "FAIL"}

                # Test 2: Log evidence validation test
                entry2 = manager.log_evidence_validation_test("EVD_001", "PASS")
                test2 = {"name": "Log evidence validation test", "result": "PASS" if entry2 is not None else "FAIL"}

                # Test 3: Log authority registration
                entry3 = manager.log_authority_registration("AUT_001", "2026-09-18T08:00:00Z")
                test3 = {"name": "Log authority registration", "result": "PASS" if entry3 is not None else "FAIL"}

                # Test 4: Log failure scenario test
                entry4 = manager.log_failure_scenario_test("EVIDENCE_MISSING", "ESC_001")
                test4 = {"name": "Log failure scenario test", "result": "PASS" if entry4 is not None else "FAIL"}

                # Test 5: Log rollback test
                entry5 = manager.log_rollback_test("CP1_001", "SUCCESS")
                test5 = {"name": "Log rollback test", "result": "PASS" if entry5 is not None else "FAIL"}

                # Test 6: Verify hash-chain integrity
                is_valid, issues = manager.verify_trail_integrity()
                test6 = {"name": "Hash-chain integrity verification", "result": "PASS" if is_valid else "FAIL"}
                if issues:
                    test6["detail"] = issues

                # Test 7: Detect retroactive insertion (should be None for valid ledger)
                retroactive = manager.ledger.detect_retroactive_insertion()
                test7 = {"name": "Retroactive insertion detection (negative test)", "result": "PASS" if retroactive is None else "FAIL"}

                # Test 8: Export audit report
                report = manager.export_audit_report()
                test8 = {"name": "Export audit report", "result": "PASS" if report["audit_report"]["total_entries"] == 5 else "FAIL"}

                self.results["A5"]["tests"] = [test1, test2, test3, test4, test5, test6, test7, test8]
                self.results["A5"]["status"] = "PASS" if all(t["result"] == "PASS" for t in [test1, test2, test3, test4, test5, test6, test7, test8]) else "FAIL"

                for test in [test1, test2, test3, test4, test5, test6, test7, test8]:
                    print(f"  {test['name']}: {test['result']}")
                    if "detail" in test:
                        print(f"    -> {test['detail']}")
                    if test["result"] == "PASS":
                        self.total_pass += 1
                    else:
                        self.total_fail += 1

            finally:
                # Cleanup temp file
                if os.path.exists(ledger_file):
                    os.remove(ledger_file)

        except Exception as e:
            self.results["A5"]["status"] = "FAIL"
            print(f"  EXCEPTION: {e}")
            self.total_fail += 1

    def run_all_tests(self):
        """Execute all component tests"""
        print("\n" + "=" * 60)
        print("HG-M3 PHASE 3 - STEP 1: CONTROLLED IMPLEMENTATION VALIDATION")
        print("=" * 60)

        self.test_A1_design_interpretation()
        self.test_A2_binding_objects()
        self.test_A3_validation_logic()
        self.test_A4_failure_handling()
        self.test_A5_audit_trail()

        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        for component in ["A1", "A2", "A3", "A4", "A5"]:
            status = self.results[component]["status"]
            test_count = len(self.results[component]["tests"])
            print(f"{component}: {status} ({test_count} tests)")

        print(f"\nTotal: {self.total_pass} PASS / {self.total_fail} FAIL")

        overall = "PASS" if self.total_fail == 0 else "FAIL"
        print(f"\nSTEP 1 OVERALL RESULT: {overall}")

        # Export results
        return {
            "step": "STEP_1_VALIDATION",
            "status": overall,
            "summary": {
                "A1_design_interpretation": self.results["A1"]["status"],
                "A2_binding_objects": self.results["A2"]["status"],
                "A3_validation_logic": self.results["A3"]["status"],
                "A4_failure_handling": self.results["A4"]["status"],
                "A5_audit_trail": self.results["A5"]["status"]
            },
            "total_pass": self.total_pass,
            "total_fail": self.total_fail,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
            "details": self.results
        }


if __name__ == "__main__":
    validator = ValidationStep1()
    results = validator.run_all_tests()

    # Save results
    output_file = Path(__file__).parent / "step1_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=True)
    print(f"\nResults saved to: {output_file}")
