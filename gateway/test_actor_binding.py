# -*- coding: utf-8 -*-
"""
Test Suite: Actor_ID Binding (Phase 2)
Ref: MoCKA Boundary Enforcement Phase 2, Section 6

Tests verify the binding between:
  X-MoCKA-Key (authenticated header) -> actor_id (canonical identity)
  Payload actor.id (untrusted) -> must match authenticated identity

All tests follow fail-closed principle:
  - Mismatch -> 403 Forbidden
  - Missing authentication -> 401 Unauthorized
  - Invalid key -> 401 Unauthorized
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from actor_binding import (
    get_authenticated_actor_id,
    verify_actor_id_binding,
    get_request_actor_id,
)


class TestActorBinding:
    """Test Actor_ID Binding implementation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.test_cases = []
        self.passed = 0
        self.failed = 0

    def record_test(self, test_name, input_data, expected, actual, evidence):
        """Record test result with evidence"""
        passed = expected == actual
        status = "PASS" if passed else "FAIL"
        if passed:
            self.passed += 1
        else:
            self.failed += 1

        self.test_cases.append({
            "name": test_name,
            "input": input_data,
            "expected": expected,
            "actual": actual,
            "status": status,
            "evidence": evidence,
        })

    # ======= Test Case 1: Normal authenticated identity + valid actor_id ======
    def test_normal_auth_normal_actor_id(self):
        """Normal case: valid key + matching actor_id"""
        api_key = "claude_executor"
        payload_actor_id = "claude"

        authenticated_actor = get_authenticated_actor_id(api_key)
        is_verified = verify_actor_id_binding(api_key, payload_actor_id)
        canonical_actor = get_request_actor_id(api_key, payload_actor_id)

        self.record_test(
            "Normal Auth + Normal actor_id",
            {"api_key": api_key, "payload_actor_id": payload_actor_id},
            expected=True,
            actual=is_verified and canonical_actor == "claude",
            evidence={
                "authenticated_actor": authenticated_actor,
                "is_verified": is_verified,
                "canonical_actor": canonical_actor,
            }
        )

    # ======= Test Case 2: actor_id missing =======
    def test_actor_id_missing(self):
        """Missing actor_id in payload"""
        api_key = "gpt_executor"
        payload_actor_id = None

        authenticated_actor = get_authenticated_actor_id(api_key)
        is_verified = verify_actor_id_binding(api_key, payload_actor_id)

        # Missing actor_id is acceptable (caller decides if required)
        # but we verify the authenticated identity can still be determined
        self.record_test(
            "actor_id missing",
            {"api_key": api_key, "payload_actor_id": None},
            expected=True,  # Should still verify (missing ≠ mismatch)
            actual=is_verified and authenticated_actor == "gpt",
            evidence={
                "authenticated_actor": authenticated_actor,
                "is_verified": is_verified,
            }
        )

    # ======= Test Case 3: Payload actor_id mismatch =======
    def test_actor_id_mismatch(self):
        """Payload actor_id doesn't match authenticated identity"""
        api_key = "claude_executor"
        payload_actor_id = "gpt"  # Wrong! Should be "claude"

        authenticated_actor = get_authenticated_actor_id(api_key)
        is_verified = verify_actor_id_binding(api_key, payload_actor_id)

        self.record_test(
            "actor_id mismatch (spoofing attempt)",
            {"api_key": api_key, "payload_actor_id": payload_actor_id},
            expected=False,  # Should fail
            actual=is_verified,
            evidence={
                "authenticated_actor": authenticated_actor,
                "payload_actor_id": payload_actor_id,
                "is_verified": is_verified,
            }
        )

    # ======= Test Case 4: Invalid X-MoCKA-Key =======
    def test_invalid_api_key(self):
        """Invalid or unknown API key"""
        api_key = "invalid_key_12345"
        payload_actor_id = "claude"

        authenticated_actor = get_authenticated_actor_id(api_key)
        is_verified = verify_actor_id_binding(api_key, payload_actor_id)

        self.record_test(
            "Invalid X-MoCKA-Key",
            {"api_key": api_key, "payload_actor_id": payload_actor_id},
            expected=False,  # Should fail
            actual=is_verified and authenticated_actor is None,
            evidence={
                "authenticated_actor": authenticated_actor,
                "is_verified": is_verified,
            }
        )

    # ======= Test Case 5: Empty/None API key =======
    def test_empty_api_key(self):
        """Empty or None API key"""
        for api_key in ["", None]:
            authenticated_actor = get_authenticated_actor_id(api_key)
            is_verified = verify_actor_id_binding(api_key, "claude")

            self.record_test(
                f"Empty API key: {repr(api_key)}",
                {"api_key": api_key},
                expected=False,
                actual=is_verified and authenticated_actor is None,
                evidence={
                    "authenticated_actor": authenticated_actor,
                    "is_verified": is_verified,
                }
            )

    # ======= Test Case 6: Whitespace in actor_id =======
    def test_actor_id_whitespace_handling(self):
        """Payload actor_id with extra whitespace should be normalized"""
        api_key = "gemini_executor"
        payload_actor_id = "  gemini  "  # With whitespace

        authenticated_actor = get_authenticated_actor_id(api_key)
        is_verified = verify_actor_id_binding(api_key, payload_actor_id)

        self.record_test(
            "actor_id with whitespace normalization",
            {"api_key": api_key, "payload_actor_id": payload_actor_id},
            expected=True,  # Should normalize and match
            actual=is_verified,
            evidence={
                "authenticated_actor": authenticated_actor,
                "payload_actor_id_normalized": payload_actor_id.strip(),
                "is_verified": is_verified,
            }
        )

    # ======= Test Case 7: Multiple different actors =======
    def test_multiple_actor_isolation(self):
        """Verify multiple actors don't cross-authenticate"""
        test_pairs = [
            ("claude_executor", "claude"),
            ("gpt_executor", "gpt"),
            ("gemini_executor", "gemini"),
            ("copilot_executor", "copilot"),
        ]

        all_pass = True
        for api_key, expected_actor in test_pairs:
            authenticated_actor = get_authenticated_actor_id(api_key)
            canonical = get_request_actor_id(api_key, expected_actor)

            test_pass = (authenticated_actor == expected_actor and canonical == expected_actor)
            all_pass = all_pass and test_pass

        self.record_test(
            "Multiple actor isolation",
            {"test_pairs": len(test_pairs)},
            expected=True,
            actual=all_pass,
            evidence={"test_pairs": test_pairs}
        )

    # ======= Test Case 8: Case sensitivity =======
    def test_actor_id_case_sensitivity(self):
        """Verify case sensitivity in actor_id matching"""
        api_key = "claude_executor"
        # Try uppercase - should NOT match (case-sensitive)
        payload_actor_id = "CLAUDE"

        is_verified = verify_actor_id_binding(api_key, payload_actor_id)

        self.record_test(
            "Case sensitivity (CLAUDE != claude)",
            {"api_key": api_key, "payload_actor_id": payload_actor_id},
            expected=False,  # Should fail (case-sensitive)
            actual=is_verified,
            evidence={
                "payload_actor_id": payload_actor_id,
                "is_verified": is_verified,
            }
        )

    def run_all_tests(self):
        """Execute all test cases"""
        self.setup_method()  # Initialize state
        self.test_normal_auth_normal_actor_id()
        self.test_actor_id_missing()
        self.test_actor_id_mismatch()
        self.test_invalid_api_key()
        self.test_empty_api_key()
        self.test_actor_id_whitespace_handling()
        self.test_multiple_actor_isolation()
        self.test_actor_id_case_sensitivity()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        return {
            "total": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "test_cases": self.test_cases,
        }


def main():
    """Run test suite"""
    suite = TestActorBinding()
    report = suite.run_all_tests()

    print("\n" + "=" * 70)
    print("Actor_ID Binding Test Report (Phase 2)")
    print("=" * 70)
    print(f"Total: {report['total']} | Passed: {report['passed']} | Failed: {report['failed']}")
    print("=" * 70)

    for test in report['test_cases']:
        status_symbol = "✓" if test['status'] == "PASS" else "✗"
        print(f"\n{status_symbol} {test['name']}: {test['status']}")
        print(f"   Input:    {test['input']}")
        print(f"   Expected: {test['expected']}")
        print(f"   Actual:   {test['actual']}")
        if test['evidence']:
            print(f"   Evidence: {json.dumps(test['evidence'], indent=2)}")

    print("\n" + "=" * 70)
    if report['failed'] == 0:
        print("Status: ALL TESTS PASSED")
    else:
        print(f"Status: {report['failed']} TESTS FAILED")
    print("=" * 70 + "\n")

    return 0 if report['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())
