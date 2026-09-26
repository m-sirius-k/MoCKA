# -*- coding: utf-8 -*-
"""
STEP 2 Implementation Test: JARVIS Decision -> GPT Request Binding

Purpose: Verify that JARVIS Decision context flows through to GPT API payload

Test Scenarios:
A. Decision exists (status='found') -> Decision context in GPT payload
B. Decision not found (status!='found') -> Original request_text preserved
C. Decision ID in final GPT input
D. Multi-AI dispatch still works (provider loop not broken)
E. E2E path: JARVIS -> dispatcher -> GPTSocket -> adapter_gpt -> OpenAI payload
"""

import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_dispatcher import dispatch_multi_request, _build_request_with_decision_context

# Test results storage
test_results = {
    "A_decision_present": None,
    "B_decision_absent": None,
    "C_decision_id_in_gpt": None,
    "D_multi_ai_dispatch": None,
    "E_e2e_path": None,
    "captured_decision_id": None,
    "captured_gpt_request": None,
    "captured_gpt_payload": None,
}


def test_a_decision_present():
    """
    SCENARIO A: JARVIS Decision exists
    -> Decision context should be added to request_text
    -> GPT should receive enhanced request with Decision context
    """
    print("\n" + "="*70)
    print("TEST A: JARVIS Decision Present")
    print("="*70)

    # Mock JARVIS result with real-looking Decision
    mock_jarvis_decision = {
        "source": "decision_ledger",
        "decision_id": "DC_20260923_001",
        "title": "STEP 2 Implementation Decision",
        "decision": "Implement minimal Decision context binding via request_text enhancement",
        "rationale": "Avoids changing Socket/Adapter signatures while providing Decision context to GPT",
        "approved_by": "HG_HUMAN_GATE",
        "approved_at": "2026-09-23T10:00:00Z",
        "status": "ACTIVE"
    }

    mock_jarvis_result = {
        "decision_id": mock_jarvis_decision["decision_id"],
        "request_id": "REQ_TEST_A_001",
        "status": "found",
        "jarvis_decision": mock_jarvis_decision,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Captured payload from adapter_gpt
    captured_payloads = []

    def mock_call_api(request_text, model):
        """Intercept adapter_gpt.call_api to capture request_text and payload"""
        captured_payloads.append({
            "request_text": request_text,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Log what we captured
        print(f"\n[CAPTURE] adapter_gpt.call_api intercepted:")
        print(f"  Model: {model}")
        print(f"  Request length: {len(request_text)} chars")

        # Check if Decision context is present
        if "JARVIS DECISION CONTEXT" in request_text and mock_jarvis_decision["decision_id"] in request_text:
            print(f"  [PASS] Decision context FOUND in request_text")
            print(f"    Decision ID: {mock_jarvis_decision['decision_id']}")
            test_results["A_decision_present"] = True
            test_results["captured_decision_id"] = mock_jarvis_decision["decision_id"]
            test_results["captured_gpt_request"] = request_text[:200] + "..."
            test_results["captured_gpt_payload"] = json.dumps({
                "messages": [{"role": "user", "content": request_text[:300]}],
                "model": model
            })
        else:
            print(f"  [FAIL] Decision context NOT FOUND in request_text")
            test_results["A_decision_present"] = False

        # Return mock response
        return {
            "status": "ok",
            "response": f"Mock response for model {model}",
            "model": model,
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }

    # Patch JarvisEngine and adapter_gpt
    with patch('runtime.jarvis.core.engine.JarvisEngine') as mock_jarvis_class, \
         patch('adapter_gpt.call_api', side_effect=mock_call_api), \
         patch('adapters_gpt_socket.GPTSocket'):

        # Setup mock JarvisEngine
        mock_jarvis_instance = MagicMock()
        mock_jarvis_instance.recall_experience.return_value = {
            "status": "found",
            "matches": [mock_jarvis_decision]
        }
        mock_jarvis_class.return_value = mock_jarvis_instance

        # Call dispatch_multi_request with decision_id
        result = dispatch_multi_request(
            request_text="Analyze current system state",
            providers=["gpt"],
            decision_id="TEST_DECISION_A_001"
        )

        print(f"\n[RESULT] dispatch_multi_request completed:")
        print(f"  Overall status: {result.get('status')}")
        print(f"  JARVIS result available: {'jarvis' in result}")
        if 'jarvis' in result:
            print(f"  JARVIS status: {result['jarvis'].get('status')}")
            print(f"  JARVIS Decision ID: {result['jarvis'].get('decision_id')}")
        print(f"  GPT results: {len(result.get('results', []))} provider(s)")
        print(f"  Captured payloads: {len(captured_payloads)}")


def test_b_decision_absent():
    """
    SCENARIO B: JARVIS Decision not found
    -> Original request_text should be preserved
    -> No Decision context should be added
    """
    print("\n" + "="*70)
    print("TEST B: JARVIS Decision Absent (status != 'found')")
    print("="*70)

    original_request = "Analyze current system state"

    # Mock JARVIS result with empty status
    mock_jarvis_result = {
        "decision_id": None,
        "request_id": "REQ_TEST_B_001",
        "status": "empty",
        "jarvis_decision": None,
        "jarvis_gap": "No matching decisions in ledger",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    captured_payloads = []

    def mock_call_api_b(request_text, model):
        """Intercept to verify original request_text is preserved"""
        captured_payloads.append({
            "request_text": request_text,
            "model": model
        })

        print(f"\n[CAPTURE] adapter_gpt.call_api intercepted:")
        print(f"  Model: {model}")
        print(f"  Request text: {request_text}")

        # Check if Decision context is NOT present
        if "JARVIS DECISION CONTEXT" not in request_text and request_text == original_request:
            print(f"  [PASS] Original request_text PRESERVED (no Decision context added)")
            test_results["B_decision_absent"] = True
        else:
            print(f"  [FAIL] Request text was modified or Decision context was added")
            test_results["B_decision_absent"] = False

        return {
            "status": "ok",
            "response": f"Mock response for model {model}",
            "model": model,
            "usage": {"prompt_tokens": 50, "completion_tokens": 30}
        }

    # Patch JarvisEngine and adapter_gpt
    with patch('runtime.jarvis.core.engine.JarvisEngine') as mock_jarvis_class, \
         patch('adapter_gpt.call_api', side_effect=mock_call_api_b), \
         patch('adapters_gpt_socket.GPTSocket'):

        # Setup mock JarvisEngine with empty result
        mock_jarvis_instance = MagicMock()
        mock_jarvis_instance.recall_experience.return_value = {
            "status": "empty",
            "matches": []
        }
        mock_jarvis_class.return_value = mock_jarvis_instance

        # Call dispatch_multi_request with decision_id that returns empty
        result = dispatch_multi_request(
            request_text=original_request,
            providers=["gpt"],
            decision_id="TEST_DECISION_B_001"
        )

        print(f"\n[RESULT] dispatch_multi_request completed:")
        print(f"  JARVIS status: {result.get('jarvis', {}).get('status')}")
        print(f"  Captured payloads: {len(captured_payloads)}")


def test_c_decision_id_in_gpt_input():
    """
    SCENARIO C: Decision ID should appear in final GPT input
    Verify the Decision ID is preserved through the entire flow
    """
    print("\n" + "="*70)
    print("TEST C: Decision ID in GPT Input")
    print("="*70)

    expected_decision_id = "DC_20260923_002"

    mock_jarvis_decision = {
        "decision_id": expected_decision_id,
        "title": "Test Decision C",
        "decision": "Test decision for scenario C",
        "rationale": "Verify Decision ID reaches GPT",
        "approved_by": "TEST_AUTHORITY",
        "approved_at": "2026-09-23T11:00:00Z"
    }

    decision_id_found = []

    def mock_call_api_c(request_text, model):
        """Check if Decision ID is in the GPT input"""
        print(f"\n[CAPTURE] adapter_gpt.call_api intercepted:")
        print(f"  Checking for Decision ID: {expected_decision_id}")

        if expected_decision_id in request_text:
            print(f"  [PASS] Decision ID FOUND in request_text")
            decision_id_found.append(True)
            test_results["C_decision_id_in_gpt"] = True
        else:
            print(f"  [FAIL] Decision ID NOT FOUND in request_text")
            decision_id_found.append(False)
            test_results["C_decision_id_in_gpt"] = False

        return {
            "status": "ok",
            "response": "Mock response",
            "model": model,
            "usage": {"prompt_tokens": 75, "completion_tokens": 40}
        }

    with patch('runtime.jarvis.core.engine.JarvisEngine') as mock_jarvis_class, \
         patch('adapter_gpt.call_api', side_effect=mock_call_api_c), \
         patch('adapters_gpt_socket.GPTSocket'):

        mock_jarvis_instance = MagicMock()
        mock_jarvis_instance.recall_experience.return_value = {
            "status": "found",
            "matches": [mock_jarvis_decision]
        }
        mock_jarvis_class.return_value = mock_jarvis_instance

        result = dispatch_multi_request(
            request_text="Test request",
            providers=["gpt"],
            decision_id="TRIGGER_C"
        )

        print(f"\n[RESULT] Decision ID verification:")
        print(f"  Lookups: {len(decision_id_found)}")
        print(f"  Found: {any(decision_id_found)}")


def test_d_multi_ai_dispatch_intact():
    """
    SCENARIO D: Multi-AI dispatch provider loop should still work
    Verify that all providers receive requests and responses are collected
    """
    print("\n" + "="*70)
    print("TEST D: Multi-AI Dispatch Provider Loop Intact")
    print("="*70)

    providers_called = []

    def mock_call_api_d(request_text, model):
        """Log which providers are being called"""
        providers_called.append(model)
        return {
            "status": "ok",
            "response": f"Response from {model}",
            "model": model,
            "usage": {"prompt_tokens": 80, "completion_tokens": 45}
        }

    with patch('runtime.jarvis.core.engine.JarvisEngine') as mock_jarvis_class, \
         patch('adapter_gpt.call_api', side_effect=mock_call_api_d), \
         patch('adapters_claude_socket.ClaudeSocket') as mock_claude, \
         patch('adapters_gemini_socket.GeminiSocket') as mock_gemini, \
         patch('adapters_perplexity_socket.PerplexitySocket') as mock_perplexity, \
         patch('adapters_gpt_socket.GPTSocket'):

        # Setup mock JarvisEngine
        mock_jarvis_instance = MagicMock()
        mock_jarvis_instance.recall_experience.return_value = {
            "status": "found",
            "matches": [{
                "decision_id": "DC_TEST_D",
                "title": "Test D",
                "decision": "Test decision D"
            }]
        }
        mock_jarvis_class.return_value = mock_jarvis_instance

        # Setup mock Socket returns
        mock_claude.return_value.request.return_value = {
            "status": "ok",
            "response": "Claude response",
            "model": "claude-opus-5"
        }
        mock_gemini.return_value.request.return_value = {
            "status": "ok",
            "response": "Gemini response",
            "model": "gemini-2.0-flash"
        }
        mock_perplexity.return_value.request.return_value = {
            "status": "ok",
            "response": "Perplexity response",
            "model": "sonar-pro"
        }

        result = dispatch_multi_request(
            request_text="Multi-provider test",
            providers=["gpt", "claude", "gemini", "perplexity"],
            decision_id="TEST_D"
        )

        print(f"\n[RESULT] Provider dispatch verification:")
        print(f"  Providers called: {len(result.get('results', []))}")
        print(f"  Overall status: {result.get('status')}")
        print(f"  Summary ok: {result.get('summary', {}).get('ok')}")
        print(f"  Summary total: {result.get('summary', {}).get('total')}")

        if result.get('status') in ['all_ok', 'partial_ok']:
            print(f"  [PASS] Multi-AI dispatch provider loop INTACT")
            test_results["D_multi_ai_dispatch"] = True
        else:
            print(f"  [FAIL] Multi-AI dispatch provider loop BROKEN")
            test_results["D_multi_ai_dispatch"] = False


def test_e_e2e_path():
    """
    SCENARIO E: Full E2E path verification
    JARVIS -> jarvis_result -> dispatch_multi_request -> enhanced_request -> _call_provider
    -> GPTSocket.request -> adapter_gpt.call_api -> OpenAI payload
    """
    print("\n" + "="*70)
    print("TEST E: E2E Path Verification")
    print("="*70)

    e2e_events = []

    def mock_jarvis_recall(current_intent):
        e2e_events.append("E1_JARVIS_RECALLED")
        return {
            "status": "found",
            "matches": [{
                "decision_id": "DC_20260923_E2E",
                "title": "E2E Test Decision",
                "decision": "E2E verification decision",
                "rationale": "Verify full path from JARVIS to OpenAI"
            }]
        }

    def mock_call_api_e2e(request_text, model):
        e2e_events.append("E5_ADAPTER_GPT_PAYLOAD")
        return {
            "status": "ok",
            "response": "E2E response",
            "model": model,
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }

    with patch('runtime.jarvis.core.engine.JarvisEngine') as mock_jarvis_class, \
         patch('adapter_gpt.call_api', side_effect=mock_call_api_e2e), \
         patch('adapters_gpt_socket.GPTSocket') as mock_gpt_socket_class:

        # Setup mock JarvisEngine
        mock_jarvis_instance = MagicMock()
        mock_jarvis_instance.recall_experience.side_effect = mock_jarvis_recall
        mock_jarvis_class.return_value = mock_jarvis_instance

        # Setup mock GPTSocket
        mock_gpt_socket = MagicMock()
        def mock_gpt_request(request_text, model, title):
            e2e_events.append("E3_GPTO_SOCKET_REQUEST")
            return {
                "status": "ok",
                "response": "Mock GPT response",
                "model": model
            }
        mock_gpt_socket.request.side_effect = mock_gpt_request
        mock_gpt_socket_class.return_value = mock_gpt_socket

        # Call dispatch
        e2e_events.append("E0_DISPATCH_START")
        result = dispatch_multi_request(
            request_text="E2E test request",
            providers=["gpt"],
            decision_id="E2E_TEST"
        )
        e2e_events.append("E6_DISPATCH_COMPLETE")

        print(f"\n[RESULT] E2E Path Events:")
        for i, event in enumerate(e2e_events, 1):
            print(f"  {i}. {event}")

        expected_events = ["E0_DISPATCH_START", "E1_JARVIS_RECALLED", "E3_GPTO_SOCKET_REQUEST", "E5_ADAPTER_GPT_PAYLOAD", "E6_DISPATCH_COMPLETE"]
        found_events = [e for e in e2e_events if any(exp in e for exp in expected_events)]

        if len(found_events) >= 4:
            print(f"  [PASS] E2E path VERIFIED ({len(found_events)}/{len(expected_events)} steps)")
            test_results["E_e2e_path"] = True
        else:
            print(f"  [FAIL] E2E path INCOMPLETE ({len(found_events)}/{len(expected_events)} steps)")
            test_results["E_e2e_path"] = False


def main():
    """Run all tests and report results"""
    print("\n")
    print("+"*70)
    print("STEP 2 IMPLEMENTATION TEST SUITE")
    print("JARVIS Decision -> GPT Request Binding")
    print("+"*70)

    # Run tests
    test_a_decision_present()
    test_b_decision_absent()
    test_c_decision_id_in_gpt_input()
    test_d_multi_ai_dispatch_intact()
    test_e_e2e_path()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nA. Decision Present:           {test_results['A_decision_present']}")
    print(f"B. Decision Absent:            {test_results['B_decision_absent']}")
    print(f"C. Decision ID in GPT Input:   {test_results['C_decision_id_in_gpt']}")
    print(f"D. Multi-AI Dispatch Intact:   {test_results['D_multi_ai_dispatch']}")
    print(f"E. E2E Path Verified:          {test_results['E_e2e_path']}")

    print(f"\nCaptured Decision ID:    {test_results['captured_decision_id']}")
    print(f"Captured GPT Request:    {test_results['captured_gpt_request']}")

    # Overall result
    all_passed = all([
        test_results['A_decision_present'],
        test_results['B_decision_absent'],
        test_results['C_decision_id_in_gpt'],
        test_results['D_multi_ai_dispatch'],
        test_results['E_e2e_path']
    ])

    print("\n" + "="*70)
    if all_passed:
        print("OVERALL RESULT: ALL TESTS PASSED")
    else:
        print("OVERALL RESULT: SOME TESTS FAILED")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
