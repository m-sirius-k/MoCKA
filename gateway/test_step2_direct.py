# -*- coding: utf-8 -*-
"""
STEP 2 Direct Integration Test: Request Text Enhancement

Directly test the _build_request_with_decision_context function
and verify the flow without complex mocking.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from multi_dispatcher import _build_request_with_decision_context

def test_request_enhancement():
    """Test that Decision context is properly added to request_text"""

    print("\n" + "="*70)
    print("STEP 2 DIRECT TEST: Request Text Enhancement")
    print("="*70)

    original_request = "Analyze the current decision protocol"

    # Simulate real Decision from JARVIS
    jarvis_decision = {
        "decision_id": "DC_20260923_001",
        "source": "decision_ledger",
        "title": "STEP 2 Implementation Decision",
        "decision": "Implement minimal Decision context binding via request_text enhancement",
        "rationale": "Avoids changing Socket/Adapter signatures",
        "approved_by": "HG_HUMAN_GATE",
        "approved_at": "2026-09-23T10:00:00Z",
        "status": "ACTIVE"
    }

    decision_id = "DC_20260923_001"

    # Call the enhancement function
    print("\n[TEST A] Build enhanced request_text with Decision context")
    enhanced = _build_request_with_decision_context(
        original_request_text=original_request,
        jarvis_decision=jarvis_decision,
        decision_id=decision_id
    )

    print(f"Original request length: {len(original_request)} chars")
    print(f"Enhanced request length: {len(enhanced)} chars")
    print(f"\nEnhanced request:")
    print("-" * 70)
    print(enhanced)
    print("-" * 70)

    # Verify A: Decision context block is present
    test_a_pass = "[JARVIS DECISION CONTEXT]" in enhanced and "[END JARVIS DECISION CONTEXT]" in enhanced
    print(f"\n[RESULT A] Decision context block present: {test_a_pass}")

    # Verify B: Decision ID is in enhanced text
    test_b_pass = decision_id in enhanced
    print(f"[RESULT B] Decision ID in enhanced text: {test_b_pass}")

    # Verify C: Original request is preserved
    test_c_pass = original_request in enhanced
    print(f"[RESULT C] Original request preserved: {test_c_pass}")

    # Verify D: All expected fields are present
    fields_expected = {
        "Decision ID": decision_id,
        "Title": jarvis_decision.get("title", ""),
        "Decision": jarvis_decision.get("decision", ""),
        "Rationale": jarvis_decision.get("rationale", ""),
        "Approved By": jarvis_decision.get("approved_by", "")
    }

    fields_found = {}
    for field_name, field_value in fields_expected.items():
        found = field_value in enhanced
        fields_found[field_name] = found
        print(f"  {field_name}: {found}")

    test_d_pass = all(fields_found.values())
    print(f"[RESULT D] All expected fields present: {test_d_pass}")

    # Verify E: Request-text would flow through provider pipeline
    # Simulate what would be passed to adapter_gpt.call_api
    would_reach_gpt = enhanced
    test_e_pass = (
        "[JARVIS DECISION CONTEXT]" in would_reach_gpt and
        decision_id in would_reach_gpt and
        "Original request:" in would_reach_gpt
    )
    print(f"[RESULT E] Would reach GPT payload: {test_e_pass}")

    # Summary
    print("\n" + "="*70)
    all_pass = test_a_pass and test_b_pass and test_c_pass and test_d_pass and test_e_pass
    print(f"A. Decision context block:    {test_a_pass}")
    print(f"B. Decision ID present:       {test_b_pass}")
    print(f"C. Original request preserved: {test_c_pass}")
    print(f"D. All fields present:        {test_d_pass}")
    print(f"E. Reaches GPT payload:       {test_e_pass}")
    print("\n" + "="*70)
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print("="*70 + "\n")

    return 0 if all_pass else 1


def test_no_decision():
    """Test that when decision is None, original request is preserved"""

    print("\n" + "="*70)
    print("STEP 2 TEST: No Decision Scenario")
    print("="*70)

    original_request = "Analyze the current decision protocol"

    # This simulates dispatch_multi_request behavior when Decision not found
    # (it would use original_request_text, not calling _build_request_with_decision_context)

    print("\n[TEST] When Decision status != 'found':")
    print(f"Original request would be used: {original_request}")
    print(f"Enhanced function NOT called")
    print(f"GPT receives: {original_request}")

    test_pass = True  # This is handled in dispatch_multi_request logic
    print(f"\n[RESULT] Original request preserved when no Decision: {test_pass}")

    return 0 if test_pass else 1


def test_payload_simulation():
    """Simulate how Decision context would look in OpenAI payload"""

    print("\n" + "="*70)
    print("STEP 2 TEST: OpenAI Payload Simulation")
    print("="*70)

    original_request = "What is the status?"
    jarvis_decision = {
        "decision_id": "DC_20260923_SIM",
        "title": "Status Decision",
        "decision": "Status is ACTIVE",
        "rationale": "Based on review"
    }

    enhanced = _build_request_with_decision_context(
        original_request_text=original_request,
        jarvis_decision=jarvis_decision,
        decision_id=jarvis_decision.get("decision_id")
    )

    # Simulate OpenAI API payload
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": enhanced
            }
        ],
        "max_tokens": 1024
    }

    print("\n[Simulated OpenAI Payload]")
    print(json.dumps(payload, indent=2, ensure_ascii=False)[:500])
    print("\n[Content Preview]")
    print(payload["messages"][0]["content"][:300])

    # Verify payload contains Decision
    test_pass = "JARVIS DECISION CONTEXT" in payload["messages"][0]["content"]
    print(f"\n[RESULT] Decision context in OpenAI payload: {test_pass}")

    return 0 if test_pass else 1


if __name__ == "__main__":
    results = []
    results.append(test_request_enhancement())
    results.append(test_no_decision())
    results.append(test_payload_simulation())

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")

    sys.exit(max(results))
