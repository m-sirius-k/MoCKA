#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GL8-GL12 Authorization Pipeline Integration
Verifies fail-fast behavior and runtime enforcement.
"""

import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from structural.governance_pipeline import GovernancePipeline
from structural.authorization_pipeline import AUTHZ_OK, AUTHZ_BYPASS_READ_ONLY
from structural.human_gate_authorization_integrity import GL8_FAIL_1
from structural.authorization_scope_binding import GL9_FAIL_1
from structural.tool_registry_enforcement import GL11_FAIL_1_UNKNOWN_TOOL


def test_gl8_gl12_read_only_tool_bypass():
    """Test Case 1: Read-only tools bypass GL8-GL12"""
    print("\n" + "=" * 80)
    print("Test 1: Read-only tool bypasses GL8-GL12")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # mocka_get_overview is in READ_ONLY_TOOLS
    # Should bypass GL8-GL12 even without _authz envelope
    decision = pipeline.before_tool("mocka_get_overview", {"param": "value"})

    print(f"Tool: mocka_get_overview")
    print(f"Authorization Result: {decision.authz_result}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")

    # Should be allowed (GL8-GL12 bypass for read-only)
    # Note: GL1-GL7 might still block, but GL8-GL12 should not be the blocker
    assert decision.authz_result == AUTHZ_BYPASS_READ_ONLY, \
        f"Expected AUTHZ_BYPASS_READ_ONLY, got {decision.authz_result}"
    print("✓ PASS: Read-only tool bypasses GL8-GL12")


def test_gl8_missing_authz_envelope():
    """Test Case 2: Write tool without _authz envelope fails GL8"""
    print("\n" + "=" * 80)
    print("Test 2: Write tool without _authz envelope fails GL8")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # mocka_write_event requires _authz envelope (GL8)
    # Call without _authz -> GL8_FAIL_1
    decision = pipeline.before_tool("mocka_write_event", {
        "title": "test event",
        "description": "test"
    })

    print(f"Tool: mocka_write_event")
    print(f"Args: no _authz envelope")
    print(f"Authorization Result: {decision.authz_result}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")

    # GL8 fails -> authorization blocked
    assert not decision.allowed, "Expected blocked due to GL8"
    assert GL8_FAIL_1 in decision.authz_result, \
        f"Expected GL8_FAIL_1 in result, got {decision.authz_result}"
    print("✓ PASS: GL8 correctly rejects missing _authz envelope")


def test_gl8_authz_present_gl9_scope_missing():
    """Test Case 3: Valid _authz with decision_id but missing scope fails GL9"""
    print("\n" + "=" * 80)
    print("Test 3: Valid _authz.decision_id but missing scope fails GL9")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # _authz with decision_id but no scope -> GL9 fails
    decision = pipeline.before_tool("mocka_write_event", {
        "title": "test event",
        "_authz": {
            "decision_id": "dec-12345"
            # missing scope -> GL9 failure
        }
    })

    print(f"Tool: mocka_write_event")
    print(f"Args: _authz.decision_id present, scope missing")
    print(f"Authorization Result: {decision.authz_result}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")

    # GL9 fails -> authorization blocked
    assert not decision.allowed, "Expected blocked due to GL9"
    assert GL9_FAIL_1 in decision.authz_result, \
        f"Expected GL9_FAIL_1 in result, got {decision.authz_result}"
    print("✓ PASS: GL9 correctly rejects missing scope")


def test_gl8_gl9_pass_unknown_tool_fails_gl11():
    """Test Case 4: Valid _authz but unknown tool fails GL11"""
    print("\n" + "=" * 80)
    print("Test 4: Valid _authz but unregistered tool fails GL11")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # Valid _authz but tool not in registry -> GL11 fails
    decision = pipeline.before_tool("unknown_tool_xyz", {
        "title": "test",
        "_authz": {
            "decision_id": "dec-12345",
            "scope": "test-scope"
        }
    })

    print(f"Tool: unknown_tool_xyz (not in registry)")
    print(f"Args: valid _authz envelope")
    print(f"Authorization Result: {decision.authz_result}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")

    # GL11 fails -> authorization blocked
    assert not decision.allowed, "Expected blocked due to GL11"
    assert GL11_FAIL_1_UNKNOWN_TOOL in decision.authz_result, \
        f"Expected GL11_FAIL_1_UNKNOWN_TOOL in result, got {decision.authz_result}"
    print("✓ PASS: GL11 correctly rejects unregistered tool")


def test_gl8_gl9_gl11_pass_authorization_ok():
    """Test Case 5: Valid _authz + registered tool passes GL8-GL12"""
    print("\n" + "=" * 80)
    print("Test 5: Valid _authz + registered tool passes GL8-GL12")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # Valid _authz with decision_id and scope, registered tool -> GL8-GL12 OK
    decision = pipeline.before_tool("mocka_write_event", {
        "title": "test event",
        "_authz": {
            "decision_id": "dec-12345",
            "scope": "test-scope"
        }
    })

    print(f"Tool: mocka_write_event (registered)")
    print(f"Args: valid _authz envelope with decision_id and scope")
    print(f"Authorization Result: {decision.authz_result}")
    print(f"Reason: {decision.reason}")

    # GL8-GL12 should pass (authorization_ok)
    assert decision.authz_result == AUTHZ_OK, \
        f"Expected AUTHZ_OK, got {decision.authz_result}"
    # Allowed depends on GL1-GL7 checks, but GL8-GL12 should not block
    print(f"GL8-GL12 passed: {decision.authz_result}")
    print("✓ PASS: GL8-GL12 accepts valid authorization")


def test_fail_fast_behavior():
    """Test Case 6: Fail-fast - GL8 failure immediately blocks without GL1-GL7"""
    print("\n" + "=" * 80)
    print("Test 6: Fail-fast behavior - GL8-GL12 failure blocks immediately")
    print("=" * 80)

    pipeline = GovernancePipeline()

    # GL8 fails due to missing _authz
    decision = pipeline.before_tool("mocka_write_event", {
        "title": "test"
        # no _authz -> GL8 fails immediately
    })

    print(f"GL8 failed: {GL8_FAIL_1 in decision.authz_result}")
    print(f"Thinking mode: {decision.thinking_mode}")

    # Verify fail-fast: thinking_mode should indicate authorization blocking
    assert decision.thinking_mode == "BLOCKED_BY_AUTHORIZATION", \
        f"Expected BLOCKED_BY_AUTHORIZATION, got {decision.thinking_mode}"
    assert not decision.allowed
    print("✓ PASS: GL8-GL12 failure causes immediate fail-fast block")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("GL8-GL12 AUTHORIZATION PIPELINE INTEGRATION TESTS")
    print("=" * 80)

    tests = [
        test_gl8_gl12_read_only_tool_bypass,
        test_gl8_missing_authz_envelope,
        test_gl8_authz_present_gl9_scope_missing,
        test_gl8_gl9_pass_unknown_tool_fails_gl11,
        test_gl8_gl9_gl11_pass_authorization_ok,
        test_fail_fast_behavior,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAIL: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
