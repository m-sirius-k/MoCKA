#!/usr/bin/env python
"""
TEST: Internal Python Authority Boundary
VERIFY: Non-HUMAN_AUTHORITY approve() calls are BLOCKED
VERIFY: Scope/target mismatch blocks authorization_state issuance
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from phi_os.human_gate import submit, approve, get_state

def test_case_a_ai_authority_blocked():
    """
    CASE-A: Direct Python approve(actor=AI, authority_role=AI_AUTHORITY)
    Expected: BLOCKED, authorization_state NOT generated
    """
    print("\n[CASE-A] AI_AUTHORITY approve() call")

    request_id = "TEST_INTERNAL_A"
    decision_id = "DC_INTERNAL_A"

    # Step 1: Submit (AI can submit)
    print("  Step 1: AI submits")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "JARVIS_AI",
        "scope": ["test"],
        "authority_role": "AI_AUTHORITY"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    # Step 2: AI tries to approve
    print("  Step 2: AI tries to approve with AI_AUTHORITY")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "JARVIS_AI",
        "scope": ["test"],
        "authority_role": "AI_AUTHORITY"  # NOT HUMAN_AUTHORITY
    })

    # Check if authorization_state was issued
    is_issued = approve_result.get("authorization_state_issued")
    validation_error = approve_result.get("authorization_validation_error")

    print(f"    State transition: {approve_result.get('next_state')}")
    print(f"    Auth state issued: {is_issued}")
    if validation_error:
        print(f"    Validation error: {validation_error}")

    if is_issued is False and "HUMAN_AUTHORITY" in str(validation_error or ""):
        print("    [OK] Authorization state BLOCKED (AI_AUTHORITY rejected)")
        return True
    else:
        print("    [FAIL] Authorization state was issued or wrong error")
        return False

def test_case_b_mcp_authority_blocked():
    """
    CASE-B: Direct Python approve(actor=MCP, authority_role=MCP_EXECUTOR)
    Expected: BLOCKED
    """
    print("\n[CASE-B] MCP_EXECUTOR approve() call")

    request_id = "TEST_INTERNAL_B"
    decision_id = "DC_INTERNAL_B"

    print("  Step 1: Submit")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "MCP_RUNNER",
        "scope": ["test"],
        "authority_role": "MCP_EXECUTOR"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    print("  Step 2: MCP tries to approve with MCP_EXECUTOR")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "MCP_RUNNER",
        "scope": ["test"],
        "authority_role": "MCP_EXECUTOR"  # NOT HUMAN_AUTHORITY
    })

    is_issued = approve_result.get("authorization_state_issued")

    print(f"    Auth state issued: {is_issued}")

    if is_issued is False:
        print("    [OK] Authorization state BLOCKED (MCP_EXECUTOR rejected)")
        return True
    else:
        print("    [FAIL] Authorization state was issued")
        return False

def test_case_c_scope_mismatch_blocked():
    """
    CASE-C: HUMAN_AUTHORITY approve with scope MISMATCH
    Expected: BLOCKED, authorization_state NOT generated
    """
    print("\n[CASE-C] Scope mismatch with HUMAN_AUTHORITY")

    request_id = "TEST_INTERNAL_C"
    decision_id = "DC_INTERNAL_C"

    print("  Step 1: Submit with scope=[scope_a]")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["scope_a"],
        "authority_role": "HUMAN_AUTHORITY"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    print("  Step 2: Approve with scope=[scope_b] (MISMATCH)")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["scope_b"],  # Different from submit!
        "authority_role": "HUMAN_AUTHORITY"
    })

    is_issued = approve_result.get("authorization_state_issued")
    validation_error = approve_result.get("authorization_validation_error")

    print(f"    Auth state issued: {is_issued}")
    if validation_error:
        print(f"    Validation error: {validation_error}")

    if is_issued is False and "scope mismatch" in str(validation_error or "").lower():
        print("    [OK] Authorization state BLOCKED (scope mismatch)")
        return True
    else:
        print("    [FAIL] Scope mismatch not detected")
        return False

def test_case_d_target_mismatch_blocked():
    """
    CASE-D: HUMAN_AUTHORITY approve with target MISMATCH
    Expected: BLOCKED
    """
    print("\n[CASE-D] Target mismatch with HUMAN_AUTHORITY")

    request_id = "TEST_INTERNAL_D"
    decision_id = "DC_INTERNAL_D"

    print("  Step 1: Submit with target=target_a")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["test"],
        "authority_role": "HUMAN_AUTHORITY",
        "target": "target_a"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    print("  Step 2: Approve with target=target_b (MISMATCH)")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["test"],
        "authority_role": "HUMAN_AUTHORITY",
        "target": "target_b"  # Different from submit!
    })

    is_issued = approve_result.get("authorization_state_issued")
    validation_error = approve_result.get("authorization_validation_error")

    print(f"    Auth state issued: {is_issued}")
    if validation_error:
        print(f"    Validation error: {validation_error}")

    if is_issued is False and "target mismatch" in str(validation_error or "").lower():
        print("    [OK] Authorization state BLOCKED (target mismatch)")
        return True
    else:
        print("    [FAIL] Target mismatch not detected")
        return False

def test_case_e_human_authority_matching_scope_target_succeeds():
    """
    CASE-E: HUMAN_AUTHORITY + matching scope/target
    Expected: APPROVED, authorization_state GENERATED
    """
    print("\n[CASE-E] HUMAN_AUTHORITY with matching scope/target")

    request_id = "TEST_INTERNAL_E"
    decision_id = "DC_INTERNAL_E"

    print("  Step 1: Submit with scope=[approved_scope], target=approved_target")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["approved_scope"],
        "authority_role": "HUMAN_AUTHORITY",
        "target": "approved_target"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    print("  Step 2: Approve with matching scope/target")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["approved_scope"],  # Match!
        "authority_role": "HUMAN_AUTHORITY",
        "target": "approved_target"  # Match!
    })

    assert approve_result.get("next_state") == "APPROVED"
    is_issued = approve_result.get("authorization_state_issued")
    authorization_id = approve_result.get("authorization_id")

    print(f"    State: {approve_result.get('next_state')}")
    print(f"    Auth state issued: {is_issued}")
    print(f"    Auth ID: {authorization_id}")

    if is_issued is True and authorization_id:
        print("    [OK] Authorization state CREATED successfully")
        return True
    else:
        print("    [FAIL] Authorization state not created")
        return False

if __name__ == "__main__":
    results = {}

    try:
        results["CASE-A: AI_AUTHORITY blocked"] = test_case_a_ai_authority_blocked()
        results["CASE-B: MCP_EXECUTOR blocked"] = test_case_b_mcp_authority_blocked()
        results["CASE-C: Scope mismatch blocked"] = test_case_c_scope_mismatch_blocked()
        results["CASE-D: Target mismatch blocked"] = test_case_d_target_mismatch_blocked()
        results["CASE-E: HUMAN_AUTHORITY succeeds"] = test_case_e_human_authority_matching_scope_target_succeeds()
    except AssertionError as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*70)
    print("INTERNAL PYTHON AUTHORITY BOUNDARY TEST RESULTS")
    print("="*70)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n{passed}/{total} tests passed")
    print("\nBOUNDARY VERIFICATION:")
    print("  - AI_AUTHORITY → authorization_state BLOCKED")
    print("  - MCP_EXECUTOR → authorization_state BLOCKED")
    print("  - Scope mismatch → authorization_state BLOCKED")
    print("  - Target mismatch → authorization_state BLOCKED")
    print("  - HUMAN_AUTHORITY + matching scope/target → APPROVED + auth_state created")

    sys.exit(0 if passed == total else 1)
