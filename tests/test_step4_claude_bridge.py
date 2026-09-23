#!/usr/bin/env python
# tests/test_step4_claude_bridge.py
# STEP 4: Claude Adapter + HAB Bridge integration verification

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "gateway"))

from phi_os.human_gate import submit, approve, get_state
from hab_bridge import HABBridge


def test_claude_bridge_contract():
    """
    STEP 4: Verify Claude can use HABBridge with same contract as GPT/Gemini.
    """
    print("\n" + "="*80)
    print("STEP 4: Claude Bridge Integration Test")
    print("="*80)

    # Step 1: Simulate Claude adapter context
    print("\n[STEP 1] Simulate Claude adapter context")
    claude_context = {
        "decision_id": None,
        "scope": ["claude", "test"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test submission from Claude",
    }
    print(f"  Scope: {claude_context['scope']}")
    print(f"  Authority Role: {claude_context['authority_role']}")
    print("  [OK] Claude context prepared")

    # Step 2: Call HABBridge (same as GPT/Gemini)
    print("\n[STEP 2] Call HABBridge.submit_from_ai()")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("claude-opus-5_Claude", claude_context)

    print(f"  Status: {bridge_result.get('status')}")
    print(f"  Request ID: {bridge_result.get('request_id')}")
    print(f"  State: {bridge_result.get('state')}")
    print(f"  Decision ID: {bridge_result.get('decision_id')}")
    print(f"  AI Identity: {bridge_result.get('ai_identity')}")

    if bridge_result.get('status') != 'ok':
        print(f"  [NG] Bridge call failed: {bridge_result.get('error')}")
        return False

    print("  [OK] HABBridge.submit_from_ai() succeeded")

    # Step 3: Verify state is PENDING
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

    # Step 4: Verify approval works
    print("\n[STEP 4] Verify HAB.approve() works for Claude decision")
    approval_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "claude-opus-5_Claude",
        "scope": ["claude", "test"],
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

    print("  [OK] HAB.approve() succeeded for Claude")

    # Step 5: Verify isolation (Claude/GPT/Gemini all separate)
    print("\n[STEP 5] Verify Claude uses same HAB Core and isolation")

    gpt_result = bridge.submit_from_ai("gpt-4_ChatGPT", {
        "decision_id": None,
        "scope": ["gpt"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test from GPT",
    })

    gemini_result = bridge.submit_from_ai("gemini-2.0-flash_Gemini", {
        "decision_id": None,
        "scope": ["gemini"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test from Gemini",
    })

    gpt_request_id = gpt_result.get('request_id')
    gpt_decision_id = gpt_result.get('decision_id')
    gemini_request_id = gemini_result.get('request_id')
    gemini_decision_id = gemini_result.get('decision_id')

    print(f"  Claude Request ID:  {request_id}")
    print(f"  GPT Request ID:     {gpt_request_id}")
    print(f"  Gemini Request ID:  {gemini_request_id}")

    # Check all use HAB Core
    all_use_hab = all(rid.startswith("HG") for rid in [request_id, gpt_request_id, gemini_request_id])
    if not all_use_hab:
        print(f"  [NG] Not all request IDs have HG prefix!")
        return False

    print("  [OK] All adapters use HAB Core (HG prefix)")

    # Check all have different request IDs
    req_ids = [request_id, gpt_request_id, gemini_request_id]
    if len(set(req_ids)) != 3:
        print(f"  [NG] Request IDs should be unique!")
        return False

    # Check all have different decision IDs
    dec_ids = [decision_id, gpt_decision_id, gemini_decision_id]
    if len(set(dec_ids)) != 3:
        print(f"  [NG] Decision IDs should be unique!")
        return False

    print(f"  Claude Decision ID: {decision_id}")
    print(f"  GPT Decision ID:    {gpt_decision_id}")
    print(f"  Gemini Decision ID: {gemini_decision_id}")
    print("  [OK] All three adapters have separate decision IDs")

    print("\n" + "="*80)
    print("STEP 4: Claude Bridge Integration - PASSED")
    print("="*80)
    print("\n[OK] Claude adapter uses same HAB Bridge contract as GPT/Gemini")
    print("[OK] Claude/GPT/Gemini all connect to HAB Common Core")
    print("[OK] All three adapters execute independently")
    print("[OK] No new Gateway/Governance code needed")

    return True


if __name__ == "__main__":
    try:
        success = test_claude_bridge_contract()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[NG] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
