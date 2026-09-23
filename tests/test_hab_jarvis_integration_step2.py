#!/usr/bin/env python
# tests/test_hab_jarvis_integration_step2.py
# STEP 2 実測: HAB → Authorization State → decision_id → JARVIS

import sys
import os
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit, approve, get_state
from governance.authorization_state_bridge import get_decision_id_from_hg_event, get_authorization_state
from runtime.jarvis.core.engine import JarvisEngine


def test_hab_to_jarvis_flow():
    """
    STEP 2: Test the flow from HAB approval to JARVIS evaluation.

    Flow:
    1. AI: HAB.submit() with decision_id in payload
    2. Human: HAB.approve()
    3. System: Extract decision_id from authorization_state
    4. System: JARVIS.evaluate(decision_id)
    5. Verify: READ-BACK all identifiers are linked
    """
    print("\n" + "="*70)
    print("STEP 2 - HAB → Authorization State → JARVIS Integration Test")
    print("="*70)

    # Test data
    decision_id_payload = "DECISION_TEST_20260922_001"
    actor_id = "TEST_AI_001"
    scope = ["test_component"]
    authority_role = "TEST_AUTHORITY"

    # Step 1: HAB.submit() - AI creates request with decision_id in payload
    print("\n[STEP 1] AI submits to HAB with decision_id")
    submit_payload = {
        "decision_id": decision_id_payload,
        "actor": actor_id,
        "scope": scope,
        "authority_role": authority_role,
        "note": "Test submission with decision_id"
    }
    submit_result = submit(submit_payload)
    request_id = submit_result["request_id"]
    event_id = submit_result["event_id"]
    hg_state = get_state(request_id)

    print(f"  request_id: {request_id}")
    print(f"  event_id: {event_id}")
    print(f"  state: {hg_state}")
    assert hg_state == "PENDING", f"Expected PENDING, got {hg_state}"
    print("  ✓ HAB.submit() successful")

    # Step 2: HAB.approve() - Human approves request
    print("\n[STEP 2] Human approves in HAB")
    approval_payload = {
        "decision_id": decision_id_payload,
        "actor": actor_id,
        "scope": scope,
        "authority_role": authority_role,
        "note": "Test approval"
    }
    approval_result = approve(request_id, approval_payload)
    hg_state = get_state(request_id)

    print(f"  state: {hg_state}")
    print(f"  authorization_id: {approval_result.get('authorization_id')}")
    print(f"  decision_id (from HAB): {approval_result.get('decision_id')}")
    assert hg_state == "APPROVED", f"Expected APPROVED, got {hg_state}"
    assert approval_result.get('authorization_state_issued'), "Authorization state not issued"
    print("  ✓ HAB.approve() successful")

    # Step 3: Extract decision_id from authorization_state
    print("\n[STEP 3] Extract decision_id from authorization_state")
    authorization_id = approval_result.get('authorization_id')
    event_id_for_lookup = approval_result.get('event_id')

    # Read back authorization_state
    auth_state = get_authorization_state(authorization_id)
    if auth_state:
        print(f"  authorization_id: {authorization_id}")
        print(f"  decision_id (from auth_state): {auth_state.get('decision_id')}")
        print(f"  subject: {auth_state.get('subject')}")
        print(f"  scope: {auth_state.get('scope')}")
        print(f"  status: {auth_state.get('status')}")
        print(f"  hg_event_source: {auth_state.get('hg_event_source')}")
        assert auth_state.get('decision_id') == decision_id_payload, \
            f"Expected {decision_id_payload}, got {auth_state.get('decision_id')}"
        print("  ✓ Authorization state record found and valid")
    else:
        print(f"  ✗ Authorization state not found for {authorization_id}")
        return False

    # Step 4: JARVIS.evaluate(decision_id)
    print("\n[STEP 4] JARVIS evaluates decision")
    extracted_decision_id = auth_state.get('decision_id')
    if not extracted_decision_id:
        print("  ✗ No decision_id to pass to JARVIS (Fail-Closed)")
        return False

    jarvis = JarvisEngine()
    jarvis_result = jarvis.evaluate(extracted_decision_id)
    print(f"  decision_id (for JARVIS): {extracted_decision_id}")
    print(f"  JARVIS.evaluate() returned: {json.dumps(jarvis_result, indent=4, ensure_ascii=False)}")
    assert jarvis_result.get('decision_id') == extracted_decision_id, \
        f"JARVIS decision_id mismatch"
    print("  ✓ JARVIS.evaluate() successful")

    # Step 5: READ-BACK verification
    print("\n[STEP 5] READ-BACK - Verify all identifiers are linked")
    readback = {
        "request_id": request_id,
        "event_id": event_id,
        "hg_state": hg_state,
        "authorization_id": authorization_id,
        "decision_id_submitted": decision_id_payload,
        "decision_id_from_auth_state": auth_state.get('decision_id'),
        "decision_id_for_jarvis": extracted_decision_id,
        "jarvis_decision_id": jarvis_result.get('decision_id'),
        "jarvis_status": jarvis_result.get('status'),
        "jarvis_authority": jarvis_result.get('authority'),
    }

    print(f"\n  Readback data:")
    for key, value in readback.items():
        print(f"    {key}: {value}")

    # Validation
    assert readback['decision_id_submitted'] == readback['decision_id_from_auth_state'], \
        "decision_id mismatch between submission and auth_state"
    assert readback['decision_id_for_jarvis'] == readback['jarvis_decision_id'], \
        "decision_id mismatch between auth_state and JARVIS"
    assert readback['hg_state'] == 'APPROVED', "HAB state not APPROVED"
    assert auth_state.get('status') == 'APPROVED', "Authorization status not APPROVED"

    print("\n  ✓ All identifiers correctly linked through the pipeline")
    print("\n" + "="*70)
    print("STEP 2 - TEST PASSED")
    print("="*70)
    print(f"\nVerified flow:")
    print(f"  AI → HAB.submit(decision_id={decision_id_payload})")
    print(f"     → HAB.approve() [request_id={request_id}]")
    print(f"     → authorization_state [authorization_id={authorization_id}]")
    print(f"     → JARVIS.evaluate(decision_id={extracted_decision_id})")
    print(f"     → READ-BACK confirms linkage ✓")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_hab_to_jarvis_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
