#!/usr/bin/env python
# tests/test_step5_perplexity_bridge.py
# STEP 5: Perplexity Adapter + HAB Bridge integration verification

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "gateway"))

from phi_os.human_gate import submit, approve, get_state
from hab_bridge import HABBridge


def test_perplexity_bridge_contract():
    """
    STEP 5: Verify Perplexity can use HABBridge with same contract as all other adapters.
    """
    print("\n" + "="*80)
    print("STEP 5: Perplexity Bridge Integration Test")
    print("="*80)

    # Step 1: Simulate Perplexity adapter context
    print("\n[STEP 1] Simulate Perplexity adapter context")
    perplexity_context = {
        "decision_id": None,
        "scope": ["perplexity", "web_search"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test web search result from Perplexity",
    }
    print(f"  Scope: {perplexity_context['scope']}")
    print(f"  Authority Role: {perplexity_context['authority_role']}")
    print("  [OK] Perplexity context prepared")

    # Step 2: Call HABBridge (same as all others)
    print("\n[STEP 2] Call HABBridge.submit_from_ai()")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("sonar-pro_Perplexity", perplexity_context)

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
    print("\n[STEP 4] Verify HAB.approve() works for Perplexity decision")
    approval_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "sonar-pro_Perplexity",
        "scope": ["perplexity", "web_search"],
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

    print("  [OK] HAB.approve() succeeded for Perplexity")

    # Step 5: Verify all 4 adapters use HAB Common Core and are isolated
    print("\n[STEP 5] Verify all 4 adapters on HAB Common Core with isolation")

    gpt_result = bridge.submit_from_ai("gpt-4_ChatGPT", {
        "decision_id": None,
        "scope": ["gpt"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test",
    })

    gemini_result = bridge.submit_from_ai("gemini-2.0-flash_Gemini", {
        "decision_id": None,
        "scope": ["gemini"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test",
    })

    claude_result = bridge.submit_from_ai("claude-opus-5_Claude", {
        "decision_id": None,
        "scope": ["claude"],
        "authority_role": "AI_AUTHORITY",
        "note": "Test",
    })

    req_ids = [
        request_id,
        gpt_result.get('request_id'),
        gemini_result.get('request_id'),
        claude_result.get('request_id'),
    ]

    dec_ids = [
        decision_id,
        gpt_result.get('decision_id'),
        gemini_result.get('decision_id'),
        claude_result.get('decision_id'),
    ]

    print(f"  Perplexity Request: {req_ids[0]}")
    print(f"  GPT Request:        {req_ids[1]}")
    print(f"  Gemini Request:     {req_ids[2]}")
    print(f"  Claude Request:     {req_ids[3]}")

    # Verify all use HAB Core
    all_use_hab = all(rid.startswith("HG") for rid in req_ids)
    if not all_use_hab:
        print(f"  [NG] Not all request IDs have HG prefix!")
        return False

    print("  [OK] All 4 adapters use HAB Core (HG prefix)")

    # Verify all have unique request IDs
    if len(set(req_ids)) != 4:
        print(f"  [NG] Request IDs should all be unique!")
        return False

    # Verify all have unique decision IDs
    if len(set(dec_ids)) != 4:
        print(f"  [NG] Decision IDs should all be unique!")
        return False

    print(f"  Perplexity Decision: {dec_ids[0]}")
    print(f"  GPT Decision:        {dec_ids[1]}")
    print(f"  Gemini Decision:     {dec_ids[2]}")
    print(f"  Claude Decision:     {dec_ids[3]}")
    print("  [OK] All 4 adapters have separate decision IDs")

    print("\n" + "="*80)
    print("STEP 5: Perplexity Bridge Integration - PASSED")
    print("="*80)
    print("\n[OK] Perplexity adapter connected to HAB Common Core")
    print("[OK] All 4 adapters (GPT/Gemini/Claude/Perplexity) on same HAB Core")
    print("[OK] All execute independently with isolated IDs")
    print("[OK] No new Gateway/Governance code needed")

    return True


if __name__ == "__main__":
    try:
        success = test_perplexity_bridge_contract()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[NG] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
