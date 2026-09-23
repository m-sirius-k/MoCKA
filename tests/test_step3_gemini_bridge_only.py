#!/usr/bin/env python
# tests/test_step3_gemini_bridge_only.py
# STEP 3: Gemini Bridge integration verification (HAB only, no Gateway)

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "gateway"))

from phi_os.human_gate import submit, approve, get_state
from hab_bridge import HABBridge


def test_gemini_bridge_contract():
    """
    STEP 3: Verify Gemini can use HABBridge with same contract as GPT.

    This test focuses on Bridge behavior only, not the full Gateway flow.
    """
    print("\n" + "="*80)
    print("STEP 3: Gemini Bridge Integration Test")
    print("="*80)

    # Simulate Gemini adapter calling HABBridge
    print("\n[STEP 1] Simulate Gemini adapter context")
    gemini_context = {
        "decision_id": None,
        "scope": ["gemini", "test"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test submission from Gemini",
    }
    print(f"  Scope: {gemini_context['scope']}")
    print(f"  Authority Role: {gemini_context['authority_role']}")
    print("  [OK] Gemini context prepared")

    # Step 2: Call HABBridge (same as GPT)
    print("\n[STEP 2] Call HABBridge.submit_from_ai()")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("gemini-2.0-flash_Gemini", gemini_context)

    print(f"  Status: {bridge_result.get('status')}")
    print(f"  Request ID: {bridge_result.get('request_id')}")
    print(f"  State: {bridge_result.get('state')}")
    print(f"  Decision ID: {bridge_result.get('decision_id')}")
    print(f"  AI Identity: {bridge_result.get('ai_identity')}")

    if bridge_result.get('status') != 'ok':
        print(f"  [NG] Bridge call failed: {bridge_result.get('error')}")
        return False

    print("  [OK] HABBridge.submit_from_ai() succeeded")

    # Step 3: Verify state is PENDING (not auto-approved)
    print("\n[STEP 3] Verify state is PENDING")
    request_id = bridge_result.get('request_id')
    decision_id = bridge_result.get('decision_id')
    state = get_state(request_id)

    print(f"  Request ID: {request_id}")
    print(f"  Decision ID: {decision_id}")
    print(f"  State: {state}")

    if state != "PENDING":
        print(f"  [NG] Expected PENDING, got {state}")
        return False

    print("  [OK] State is PENDING (Bridge did not auto-approve)")

    # Step 4: Verify approval works (same contract as GPT)
    print("\n[STEP 4] Verify HAB.approve() works for Gemini decision")
    approval_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "gemini-2.0-flash_Gemini",
        "scope": ["gemini", "test"],
        "authority_role": "AI_AUTHORITY",
    })

    auth_id = approval_result.get('authorization_id')
    print(f"  Authorization ID: {auth_id}")

    if not auth_id:
        print(f"  [NG] Approval failed: {approval_result}")
        return False

    new_state = get_state(request_id)
    print(f"  New State: {new_state}")

    if new_state != "APPROVED":
        print(f"  [NG] Expected APPROVED, got {new_state}")
        return False

    print("  [OK] HAB.approve() succeeded for Gemini")

    # Step 5: Verify same HAB Common Core as GPT
    print("\n[STEP 5] Verify Gemini uses same HAB Core as GPT")

    # Test with GPT context
    gpt_context = {
        "decision_id": None,
        "scope": ["gpt", "test"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test from GPT",
    }

    gpt_result = bridge.submit_from_ai("gpt-4_ChatGPT", gpt_context)
    gpt_request_id = gpt_result.get('request_id')
    gpt_decision_id = gpt_result.get('decision_id')

    print(f"  Gemini Request ID: {request_id}")
    print(f"  GPT Request ID: {gpt_request_id}")
    print(f"  Same Request ID prefix: {request_id[:2] == gpt_request_id[:2]}")
    print(f"  Both PENDING: {get_state(request_id) == get_state(gpt_request_id) == 'PENDING'}")

    if request_id == gpt_request_id:
        print(f"  [NG] Request IDs should be different!")
        return False

    if not (request_id.startswith("HG") and gpt_request_id.startswith("HG")):
        print(f"  [NG] Both should start with HG prefix (HAB signature)")
        return False

    print("  [OK] Both Gemini and GPT use HAB Common Core (same prefix, different IDs)")

    # Step 6: Verify isolation (Gemini and GPT are separate)
    print("\n[STEP 6] Verify Gemini/GPT isolation")

    if decision_id == gpt_decision_id:
        print(f"  [NG] Decision IDs should be different!")
        return False

    print(f"  Gemini Decision ID: {decision_id}")
    print(f"  GPT Decision ID: {gpt_decision_id}")
    print("  [OK] Gemini and GPT have separate decision IDs")

    print("\n" + "="*80)
    print("STEP 3: Gemini Bridge Integration - PASSED")
    print("="*80)
    print("\n[OK] Gemini adapter uses same HAB Bridge contract as GPT")
    print("[OK] Both adapters connect to HAB Common Core")
    print("[OK] Gemini and GPT execute independently")
    print("[OK] No new Gateway/Governance code needed")

    return True


if __name__ == "__main__":
    try:
        success = test_gemini_bridge_contract()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[NG] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
