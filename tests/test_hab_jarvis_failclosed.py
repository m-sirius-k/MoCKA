#!/usr/bin/env python
# tests/test_hab_jarvis_failclosed.py
# STEP 2: Fail-Closed validation - ensure JARVIS not reached in error cases

import sys
import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit, approve, reject, get_state
from governance.authorization_state_bridge import get_authorization_state, query_authorization_state


def test_no_decision_id():
    """
    Fail-Closed: decision_idなし → JARVIS へ進まない
    """
    print("\n[TEST 1] Fail-Closed: decision_id なし")
    submit_payload = {
        "actor": "TEST_AI_002",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
        # decision_id intentionally missing
    }
    submit_result = submit(submit_payload)
    request_id = submit_result["request_id"]

    approval_payload = {
        "actor": "TEST_AI_002",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
    }
    approval_result = approve(request_id, approval_payload)

    decision_id = approval_result.get('decision_id')
    print(f"  decision_id: {decision_id}")
    assert decision_id is None, "decision_id should be None when not provided"
    print("  ✓ Correctly blocked: decision_id is None, JARVIS not reached")
    return True


def test_rejected_authorization():
    """
    Fail-Closed: authorization REJECTED → JARVIS へ進まない
    """
    print("\n[TEST 2] Fail-Closed: authorization REJECTED")
    submit_payload = {
        "decision_id": "DECISION_REJECT_001",
        "actor": "TEST_AI_003",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
    }
    submit_result = submit(submit_payload)
    request_id = submit_result["request_id"]

    reject_result = reject(request_id, {"reason": "Test rejection"})
    hg_state = get_state(request_id)

    print(f"  HAB state: {hg_state}")
    assert hg_state == "REJECTED", f"Expected REJECTED, got {hg_state}"

    # Check authorization_state was not created
    auth_records = query_authorization_state(status="REJECTED")
    print(f"  Authorization records with REJECTED status: {len(auth_records)}")
    assert len(auth_records) == 0, "No authorization_state should be created for REJECTED"
    print("  ✓ Correctly blocked: no authorization_state for rejected request")
    return True


def test_pending_not_approved():
    """
    Fail-Closed: authorization PENDING (not approved) → JARVIS へ進まない
    """
    print("\n[TEST 3] Fail-Closed: authorization PENDING (not approved)")
    submit_payload = {
        "decision_id": "DECISION_PENDING_001",
        "actor": "TEST_AI_004",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
    }
    submit_result = submit(submit_payload)
    request_id = submit_result["request_id"]

    hg_state = get_state(request_id)
    print(f"  HAB state: {hg_state}")
    assert hg_state == "PENDING", f"Expected PENDING, got {hg_state}"

    # Check authorization_state was not created (only created on APPROVED)
    auth_records = query_authorization_state(decision_id="DECISION_PENDING_001")
    print(f"  Authorization records for this decision: {len(auth_records)}")
    assert len(auth_records) == 0, "No authorization_state should exist while PENDING"
    print("  ✓ Correctly blocked: no authorization_state while PENDING")
    return True


def test_approve_without_decision_id():
    """
    Fail-Closed: approval without decision_id in payload
    Decision_id is in authorization_state but will be None
    """
    print("\n[TEST 4] Fail-Closed: approve without decision_id in payload")
    submit_payload = {
        "actor": "TEST_AI_005",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
        # No decision_id
    }
    submit_result = submit(submit_payload)
    request_id = submit_result["request_id"]

    approval_payload = {
        "actor": "TEST_AI_005",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY"
        # No decision_id
    }
    approval_result = approve(request_id, approval_payload)

    authorization_id = approval_result.get('authorization_id')
    if authorization_id:
        auth_state = get_authorization_state(authorization_id)
        decision_id = auth_state.get('decision_id') if auth_state else None
    else:
        decision_id = None

    print(f"  authorization_id: {authorization_id}")
    print(f"  decision_id in auth_state: {decision_id}")
    assert decision_id is None, "decision_id should be None when not provided"
    print("  ✓ Correctly blocked: decision_id is None, JARVIS not reached")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STEP 2 - Fail-Closed Validation Tests")
    print("="*70)

    tests = [
        test_no_decision_id,
        test_rejected_authorization,
        test_pending_not_approved,
        test_approve_without_decision_id,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"Fail-Closed Tests: {passed} passed, {failed} failed")
    print("="*70 + "\n")

    sys.exit(0 if failed == 0 else 1)
