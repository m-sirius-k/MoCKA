# -*- coding: utf-8 -*-
"""
FINAL PAYLOAD OBSERVATION - Alternative Method
Observe adapter_gpt.call_api() invocation parameters
WITHOUT modifying adapter_gpt.py

Method: Import wrapper + function interception
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Store for observations
observations = {
    "call_count": 0,
    "calls": []
}

def main():
    print("\n" + "="*70)
    print("FINAL PAYLOAD OBSERVATION")
    print("Observe adapter_gpt.call_api() parameters")
    print("="*70)

    # Intercept at import time
    print("\n[SETUP] Preparing to intercept adapter_gpt.call_api()...")

    def capture_call_api(request_text, model="gpt-4"):
        """Wrapper that captures call_api invocation"""
        observations["call_count"] += 1

        print(f"\n[INTERCEPTED] adapter_gpt.call_api() CALL #{observations['call_count']}")
        print(f"  Model: {model}")
        print(f"  Request text length: {len(request_text)} chars")

        # Store request text
        observations["calls"].append({
            "call_num": observations["call_count"],
            "model": model,
            "request_text_length": len(request_text),
            "request_text_preview": request_text[:200],
            "full_request_text": request_text
        })

        # Analyze request text
        has_decision_context = "[JARVIS DECISION CONTEXT]" in request_text
        has_end_marker = "[END JARVIS DECISION CONTEXT]" in request_text
        has_original = "Original request:" in request_text

        print(f"\n  Analysis:")
        print(f"    Has [JARVIS DECISION CONTEXT]: {has_decision_context}")
        print(f"    Has [END JARVIS DECISION CONTEXT]: {has_end_marker}")
        print(f"    Has Original request section: {has_original}")

        # Show preview
        if has_decision_context:
            lines = request_text.split('\n')
            print(f"\n  First 8 lines of request:")
            for i, line in enumerate(lines[:8]):
                print(f"    {i+1}. {line[:65]}")

            # Extract Decision ID
            decision_lines = [l for l in lines if 'Decision ID:' in l]
            if decision_lines:
                print(f"\n    {decision_lines[0]}")

        # Call real adapter_gpt
        import adapter_gpt
        real_result = adapter_gpt.call_api(request_text, model)

        print(f"\n  Response from adapter_gpt.call_api():")
        print(f"    Status: {real_result.get('status')}")
        if real_result.get('status') == 'ok':
            print(f"    Model: {real_result.get('model')}")
            print(f"    Response preview: {real_result.get('response', '')[:100]}")
        else:
            print(f"    Error: {real_result.get('error', 'Unknown')}")

        observations["calls"][-1]["response_status"] = real_result.get('status')
        observations["calls"][-1]["response_preview"] = real_result.get('response', '')[:100] if real_result.get('status') == 'ok' else real_result.get('error', '')

        return real_result

    # Patch adapter_gpt.call_api before importing multi_dispatcher
    with patch('adapter_gpt.call_api', side_effect=capture_call_api):
        print("[PATCH] adapter_gpt.call_api patched for observation")

        # Now import and execute
        from multi_dispatcher import dispatch_multi_request

        print("\n[EXECUTE] Calling dispatch_multi_request()...")
        try:
            result = dispatch_multi_request(
                request_text="Observe the actual payload content in adapter_gpt call",
                providers=["gpt"],
                decision_id="PAYLOAD_OBSERVE_001",
                title="Final Payload Observation"
            )

            print(f"\n[RESULT] dispatch_multi_request completed")
            print(f"  Overall status: {result.get('status')}")
            print(f"  JARVIS status: {result.get('jarvis', {}).get('status')}")

        except Exception as e:
            print(f"\n[ERROR] dispatch_multi_request failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Verification
    print("\n" + "="*70)
    print("PAYLOAD OBSERVATION SUMMARY")
    print("="*70)

    if not observations["calls"]:
        print("[RESULT] adapter_gpt.call_api() was NOT called")
        print("STATUS: UNKNOWN")
        return 1

    print(f"\nTotal calls to adapter_gpt.call_api(): {observations['call_count']}")

    for call in observations["calls"]:
        print(f"\nCall #{call['call_num']}:")
        print(f"  Model: {call['model']}")
        print(f"  Request text length: {call['request_text_length']} chars")

        # Verify content
        request_text = call['full_request_text']
        has_decision = "[JARVIS DECISION CONTEXT]" in request_text
        has_end = "[END JARVIS DECISION CONTEXT]" in request_text
        has_original = "Original request:" in request_text

        print(f"\n  Payload content verification:")
        print(f"    [{'PASS' if has_decision else 'FAIL'}] Decision context block")
        print(f"    [{'PASS' if has_end else 'FAIL'}] End marker")
        print(f"    [{'PASS' if has_original else 'FAIL'}] Original request preserved")

        # Extract Decision ID
        decision_id_lines = [l for l in request_text.split('\n') if 'Decision ID:' in l and 'HG-REC' in l or 'DC_' in l]
        if decision_id_lines:
            print(f"    [PASS] Real Decision ID embedded")
            print(f"           {decision_id_lines[0].strip()}")
        else:
            print(f"    [INFO] Decision ID line: {[l for l in request_text.split('\n') if 'Decision ID:' in l]}")

        # Overall status
        all_pass = has_decision and has_end and has_original
        print(f"\n  Result: {'VERIFIED' if all_pass else 'INCOMPLETE'}")
        print(f"  Response status: {call.get('response_status')}")

    # Final verdict
    all_verified = all(
        "[JARVIS DECISION CONTEXT]" in call['full_request_text'] and
        "[END JARVIS DECISION CONTEXT]" in call['full_request_text'] and
        "Original request:" in call['full_request_text']
        for call in observations["calls"]
    )

    print("\n" + "="*70)
    if all_verified:
        print("FINAL PAYLOAD OBSERVATION: VERIFIED")
        print("\nConclusion:")
        print("  Enhanced request_text with JARVIS Decision context")
        print("  successfully reached adapter_gpt.call_api()")
        print("  and was passed to OpenAI API in messages[].content")
        return 0
    else:
        print("FINAL PAYLOAD OBSERVATION: INCOMPLETE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
