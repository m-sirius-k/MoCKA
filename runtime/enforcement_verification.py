"""
enforcement_verification.py
Phase 5.0 Runtime Enforcement Evidence Verification

Purpose:
  Execute STEP 3-7: Positive/Negative tests to prove that unauthorized operations
  are BLOCKED at runtime while authorized operations proceed normally.

Implementation:
  - STEP 3: Positive test (authorized execution)
  - STEP 4: Negative test A (no authorization)
  - STEP 5: Negative test B (scope violation)
  - STEP 6: Negative test C (decision integrity violation)
  - STEP 7: Negative test D (gate bypass attempt)
  - STEP 8: Read-back verification

Usage (Windows):
  cd C:\\Users\\sirok\\MoCKA
  python runtime/enforcement_verification.py

Output:
  Human_Gate_Runtime_Enforcement_Evidence_v1.json
"""

import json
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime

base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path / "structural"))

try:
    from governance_pipeline import GovernancePipeline
except ImportError as e:
    print(f"ERROR: GovernancePipeline not available: {e}")
    print(f"sys.path[0]: {sys.path[0]}")
    print(f"structural exists: {(base_path / 'structural').exists()}")
    print(f"governance_pipeline.py exists: {(base_path / 'structural' / 'governance_pipeline.py').exists()}")
    sys.exit(1)


class EnforcementTestSuite:
    def __init__(self):
        self.pipeline = GovernancePipeline()
        self.results = {
            "test_run_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tests": {}
        }

    def test_positive_authorized_execution(self):
        """
        STEP 3: Positive Test

        Setup: Valid authorization with proper decision_id and scope
        Execution: Call before_tool() for mocka_write_event
        Expected: decision.allowed == True
        Evidence: reason == "ok"
        """
        test_name = "POSITIVE_TEST_AUTHORIZED_EXECUTION"

        # Simulate authorized request with decision_id
        args = {
            "title": "Authorized Event",
            "description": "This operation should be allowed",
            "decision_id": "DC_20261002_001",
            "scope": "internal"
        }

        try:
            decision = self.pipeline.before_tool("mocka_write_event", args)

            result = {
                "status": "EXECUTED",
                "allowed": decision.allowed,
                "reason": decision.reason,
                "thinking_mode": decision.thinking_mode,
                "checklist_ok": decision.checklist_ok,
                "dry_run_aborts": decision.dry_run_aborts,
                "expected": True,
                "passed": decision.allowed == True
            }

            self.results["tests"][test_name] = result
            print(f"\n[STEP 3 - POSITIVE] {test_name}")
            print(f"  Allowed: {decision.allowed}")
            print(f"  Reason: {decision.reason}")
            print(f"  PASS: {result['passed']}")

            return result['passed']
        except Exception as e:
            result = {
                "status": "ERROR",
                "exception": str(e),
                "expected": True,
                "passed": False
            }
            self.results["tests"][test_name] = result
            print(f"\n[STEP 3 - ERROR] {e}")
            return False

    def test_negative_no_authorization(self):
        """
        STEP 4: Negative Test A

        Setup: NO authorization (no decision_id)
        Execution: Call before_tool() for mocka_write_event
        Expected: decision.allowed == False
        Evidence: reason contains "authorization" or "GL7"
        """
        test_name = "NEGATIVE_TEST_NO_AUTHORIZATION"

        args = {
            "title": "Unauthorized Event",
            "description": "No decision_id provided - should be blocked"
        }

        try:
            decision = self.pipeline.before_tool("mocka_write_event", args)

            result = {
                "status": "EXECUTED",
                "allowed": decision.allowed,
                "reason": decision.reason,
                "thinking_mode": decision.thinking_mode,
                "expected": False,
                "passed": decision.allowed == False
            }

            self.results["tests"][test_name] = result
            print(f"\n[STEP 4 - NEGATIVE A] {test_name}")
            print(f"  Allowed: {decision.allowed}")
            print(f"  Reason: {decision.reason}")
            print(f"  PASS (blocked): {result['passed']}")

            return result['passed']
        except Exception as e:
            result = {
                "status": "ERROR",
                "exception": str(e),
                "expected": False,
                "passed": False
            }
            self.results["tests"][test_name] = result
            print(f"\n[STEP 4 - ERROR] {e}")
            return False

    def test_negative_scope_violation(self):
        """
        STEP 5: Negative Test B

        Setup: Authorized with decision_id but SCOPE MISMATCH
        Decision: target=A
        Execution: target=B (different)
        Expected: decision.allowed == False
        Evidence: dry_run_aborts contains scope violation
        """
        test_name = "NEGATIVE_TEST_SCOPE_VIOLATION"

        # Simulate scope mismatch
        args = {
            "title": "Scope Violation Test",
            "description": "Scope says A but trying to write B",
            "decision_id": "DC_20261002_002",
            "requested_scope": "target_B",
            "authorized_scope": "target_A"
        }

        try:
            decision = self.pipeline.before_tool("mocka_update_todo", args)

            result = {
                "status": "EXECUTED",
                "allowed": decision.allowed,
                "reason": decision.reason,
                "dry_run_aborts": decision.dry_run_aborts,
                "expected": False,
                "passed": decision.allowed == False
            }

            self.results["tests"][test_name] = result
            print(f"\n[STEP 5 - NEGATIVE B] {test_name}")
            print(f"  Allowed: {decision.allowed}")
            print(f"  Reason: {decision.reason}")
            print(f"  PASS (blocked): {result['passed']}")

            return result['passed']
        except Exception as e:
            result = {
                "status": "ERROR",
                "exception": str(e),
                "expected": False,
                "passed": False
            }
            self.results["tests"][test_name] = result
            print(f"\n[STEP 5 - ERROR] {e}")
            return False

    def test_negative_decision_tampering(self):
        """
        STEP 6: Negative Test C

        Setup: Decision ID is valid but DECISION_INTEGRITY violation
        Decision: ID same, but content modified after approval
        Expected: decision.allowed == False
        Evidence: Integrity check fails
        """
        test_name = "NEGATIVE_TEST_DECISION_INTEGRITY_VIOLATION"

        args = {
            "title": "Decision Tampering Attempt",
            "description": "Valid ID but modified content",
            "decision_id": "DC_20261002_003",
            "decision_content_hash": "wrong_hash_after_modification"
        }

        try:
            decision = self.pipeline.before_tool("mocka_write_event", args)

            result = {
                "status": "EXECUTED",
                "allowed": decision.allowed,
                "reason": decision.reason,
                "expected": False,
                "passed": decision.allowed == False
            }

            self.results["tests"][test_name] = result
            print(f"\n[STEP 6 - NEGATIVE C] {test_name}")
            print(f"  Allowed: {decision.allowed}")
            print(f"  Reason: {decision.reason}")
            print(f"  PASS (blocked): {result['passed']}")

            return result['passed']
        except Exception as e:
            result = {
                "status": "ERROR",
                "exception": str(e),
                "expected": False,
                "passed": False
            }
            self.results["tests"][test_name] = result
            print(f"\n[STEP 6 - ERROR] {e}")
            return False

    def test_negative_bypass_attempts(self):
        """
        STEP 7: Negative Test D

        Setup: Multiple bypass attempts
        - Direct read-only tool (should pass)
        - Unknown tool (should block - Default Deny)
        - Governed tool without authorization (should block)

        Expected: Unknown tools BLOCKED by Default Deny
        """
        test_name = "NEGATIVE_TEST_BYPASS_ATTEMPTS"

        bypass_attempts = [
            {
                "name": "unknown_tool_1",
                "args": {"data": "malicious"},
                "expect_blocked": True
            },
            {
                "name": "mocka_get_overview",
                "args": {},
                "expect_blocked": False  # This is READ_ONLY
            },
            {
                "name": "custom_ai_dispatcher",
                "args": {"action": "write"},
                "expect_blocked": True
            }
        ]

        results_detail = []
        all_passed = True

        for attempt in bypass_attempts:
            try:
                decision = self.pipeline.before_tool(attempt["name"], attempt["args"])

                is_blocked = not decision.allowed
                expected_blocked = attempt["expect_blocked"]
                passed = (is_blocked == expected_blocked)
                all_passed = all_passed and passed

                results_detail.append({
                    "tool": attempt["name"],
                    "blocked": is_blocked,
                    "expected_blocked": expected_blocked,
                    "passed": passed,
                    "reason": decision.reason
                })

                print(f"\n  Bypass Attempt: {attempt['name']}")
                print(f"    Blocked: {is_blocked} (expected: {expected_blocked})")
                print(f"    PASS: {passed}")

            except Exception as e:
                results_detail.append({
                    "tool": attempt["name"],
                    "error": str(e),
                    "expected_blocked": attempt["expect_blocked"],
                    "passed": False
                })
                all_passed = False
                print(f"\n  ERROR on {attempt['name']}: {e}")

        result = {
            "status": "EXECUTED",
            "bypass_attempts": results_detail,
            "all_blocked_as_expected": all_passed,
            "passed": all_passed
        }

        self.results["tests"][test_name] = result
        print(f"\n[STEP 7 - NEGATIVE D] {test_name}")
        print(f"  All bypass attempts blocked as expected: {all_passed}")
        print(f"  PASS: {result['passed']}")

        return all_passed

    def test_read_back_verification(self):
        """
        STEP 8: Read-Back Verification

        Purpose: Verify that event tracing chain is intact
        Check: Can we trace attempt -> authorization -> decision -> result -> event?

        This is a structural test (actual DB queries would need live mocka_mcp_server)
        """
        test_name = "READ_BACK_VERIFICATION"

        try:
            # Check if event read-back mechanism is available
            from pathlib import Path
            mcp_server_path = Path(__file__).parent.parent / "mocka_mcp_server.py"
            mcp_content = mcp_server_path.read_text()

            has_verify_event_written = "_verify_event_written" in mcp_content
            has_db_read_events = "_db_read_events" in mcp_content
            has_event_store = "events.db" in mcp_content or "mocka_events.db" in mcp_content

            result = {
                "status": "VERIFIED",
                "verify_event_written_present": has_verify_event_written,
                "db_read_events_present": has_db_read_events,
                "event_store_path_present": has_event_store,
                "infrastructure_ready": all([
                    has_verify_event_written,
                    has_db_read_events,
                    has_event_store
                ]),
                "passed": all([
                    has_verify_event_written,
                    has_db_read_events,
                    has_event_store
                ])
            }

            self.results["tests"][test_name] = result
            print(f"\n[STEP 8 - READ-BACK] {test_name}")
            print(f"  _verify_event_written: {has_verify_event_written}")
            print(f"  _db_read_events: {has_db_read_events}")
            print(f"  Event store infrastructure: {has_event_store}")
            print(f"  PASS (infrastructure ready): {result['passed']}")

            return result['passed']
        except Exception as e:
            result = {
                "status": "ERROR",
                "exception": str(e),
                "passed": False
            }
            self.results["tests"][test_name] = result
            print(f"\n[STEP 8 - ERROR] {e}")
            return False

    def run_all_tests(self):
        """Execute all test steps"""
        print("\n" + "="*70)
        print("PHASE 5.0 RUNTIME ENFORCEMENT EVIDENCE VERIFICATION")
        print("="*70)

        test_results = []

        test_results.append(("STEP 3", self.test_positive_authorized_execution()))
        test_results.append(("STEP 4", self.test_negative_no_authorization()))
        test_results.append(("STEP 5", self.test_negative_scope_violation()))
        test_results.append(("STEP 6", self.test_negative_decision_tampering()))
        test_results.append(("STEP 7", self.test_negative_bypass_attempts()))
        test_results.append(("STEP 8", self.test_read_back_verification()))

        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed_count = sum(1 for _, passed in test_results if passed)
        total_count = len(test_results)

        for step, passed in test_results:
            status = "PASS" if passed else "FAIL"
            print(f"{step}: {status}")

        print(f"\nTotal: {passed_count}/{total_count} passed")

        # Add summary to results
        self.results["summary"] = {
            "total_tests": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "success_rate": f"{(passed_count/total_count)*100:.1f}%"
        }

        return passed_count == total_count

    def save_results(self):
        """Save test results to JSON"""
        output_path = Path(__file__).parent.parent / "Human_Gate_Runtime_Enforcement_Evidence_v1.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\nResults saved to: {output_path}")
        return output_path


def main():
    suite = EnforcementTestSuite()
    success = suite.run_all_tests()
    output_path = suite.save_results()

    if success:
        print("\n[SUCCESS] All enforcement tests passed!")
        print(f"Evidence artifact: {output_path}")
        return 0
    else:
        print("\n[FAILURE] Some tests failed - enforcement gaps detected")
        print(f"Evidence artifact: {output_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
