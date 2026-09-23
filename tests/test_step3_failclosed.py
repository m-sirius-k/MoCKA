#!/usr/bin/env python
# tests/test_step3_failclosed.py
# STEP 3: Fail-Closed validation

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit, reject, get_state
from runtime.jarvis.core.engine import JarvisEngine


def test_fail_closed():
    """
    STEP 3 Fail-Closed validation:
    - No authorization -> JARVIS denies
    - Authorization PENDING -> JARVIS denies
    - Authorization REJECTED -> JARVIS denies
    - decision_id mismatch -> JARVIS denies
    """
    print("\n" + "="*80)
    print("STEP 3 - Fail-Closed Validation")
    print("="*80)

    jarvis = JarvisEngine(runtime_url="http://localhost:5000")
    passed = 0
    failed = 0

    # Test 1: No authorization
    print("\n[TEST 1] No authorization for decision_id")
    result = jarvis.receive_decision_from_hab("NONEXISTENT_DC_001")
    print(f"  Status: {result.get('status')}")
    print(f"  Reason: {result.get('reason')}")
    print(f"  execution_id: {result.get('execution_id')}")

    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print("  ✓ PASS: Correctly denied")
        passed += 1
    else:
        print("  ✗ FAIL: Should be DENIED with no execution_id")
        failed += 1

    # Test 2: Authorization PENDING (not approved)
    print("\n[TEST 2] Authorization PENDING (not approved)")
    decision_id_pending = f"DC_PENDING_{__import__('uuid').uuid4().hex[:8]}"
    submit_result = submit({
        "decision_id": decision_id_pending,
        "actor": "TEST_AI",
        "scope": ["test"],
        "authority_role": "TEST_AUTH",
    })
    request_id = submit_result["request_id"]
    state = get_state(request_id)
    print(f"  HAB state: {state}")

    result = jarvis.receive_decision_from_hab(decision_id_pending)
    print(f"  JARVIS Status: {result.get('status')}")
    print(f"  Reason: {result.get('reason')}")

    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print("  ✓ PASS: Correctly denied (PENDING)")
        passed += 1
    else:
        print("  ✗ FAIL: Should be DENIED while PENDING")
        failed += 1

    # Test 3: Authorization REJECTED
    print("\n[TEST 3] Authorization REJECTED")
    decision_id_rejected = f"DC_REJECTED_{__import__('uuid').uuid4().hex[:8]}"
    submit_result = submit({
        "decision_id": decision_id_rejected,
        "actor": "TEST_AI",
        "scope": ["test"],
        "authority_role": "TEST_AUTH",
    })
    request_id = submit_result["request_id"]

    reject(request_id, {"reason": "Test rejection"})
    state = get_state(request_id)
    print(f"  HAB state: {state}")

    result = jarvis.receive_decision_from_hab(decision_id_rejected)
    print(f"  JARVIS Status: {result.get('status')}")
    print(f"  Reason: {result.get('reason')}")

    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print("  ✓ PASS: Correctly denied (REJECTED)")
        passed += 1
    else:
        print("  ✗ FAIL: Should be DENIED when HAB state is REJECTED")
        failed += 1

    # Test 4: decision_id mismatch in authorization_state
    print("\n[TEST 4] decision_id mismatch")
    print("  (Simulated by checking a different decision_id)")

    # Submit with decision_id_A, then check with decision_id_B
    from governance.authorization_state_bridge import query_authorization_state
    from phi_os.human_gate import approve

    decision_id_mismatch = f"DC_MISMATCH_{__import__('uuid').uuid4().hex[:8]}"
    submit_result = submit({
        "decision_id": decision_id_mismatch,
        "actor": "TEST_AI",
        "scope": ["test"],
        "authority_role": "TEST_AUTH",
    })
    request_id = submit_result["request_id"]

    approval_result = approve(request_id, {
        "decision_id": decision_id_mismatch,
        "actor": "TEST_AI",
        "scope": ["test"],
        "authority_role": "TEST_AUTH",
    })

    # Now try with a different decision_id
    different_decision_id = f"DC_DIFFERENT_{__import__('uuid').uuid4().hex[:8]}"
    result = jarvis.receive_decision_from_hab(different_decision_id)
    print(f"  JARVIS Status: {result.get('status')}")
    print(f"  Reason: {result.get('reason')}")

    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print("  ✓ PASS: Correctly denied (decision_id mismatch)")
        passed += 1
    else:
        print("  ✗ FAIL: Should be DENIED when decision_id not found")
        failed += 1

    # Summary
    print("\n" + "="*80)
    print(f"Fail-Closed Tests: {passed} passed, {failed} failed")
    print("="*80 + "\n")

    return failed == 0


if __name__ == "__main__":
    try:
        success = test_fail_closed()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
