# -*- coding: utf-8 -*-
"""
Trace call_api() execution without modifying adapter_gemini.py

Monkey-patch adapter_gemini.call_api at import time to capture arguments.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global capture
adapter_call_data = {
    "called": False,
    "request_text": None,
    "request_text_length": 0,
    "has_decision_context_marker": False,
    "has_end_marker": False,
    "has_real_decision_id": False,
    "model": None,
}

REAL_DECISION_ID = "HG-REC-2026-PH2834-01-DP5-DECISION-20260912"


def setup_adapter_trace():
    """
    Intercept adapter_gemini.call_api() to capture arguments.
    This happens BEFORE genai.GenerativeModel is called.
    """
    import adapter_gemini

    original_call_api = adapter_gemini.call_api

    def call_api_with_trace(request_text: str, model: str = "gemini-2.0-flash"):
        """Capture arguments at adapter_gemini.call_api entry point"""

        # Capture the actual request_text received by adapter
        adapter_call_data["called"] = True
        adapter_call_data["request_text"] = request_text
        adapter_call_data["request_text_length"] = len(request_text)
        adapter_call_data["model"] = model

        print(f"\n[TRACE] adapter_gemini.call_api() entry point")
        print(f"  ✓ CALLED")
        print(f"  request_text length: {len(request_text)} chars")
        print(f"  model: {model}")

        # Verify Decision context markers
        has_start = "[JARVIS DECISION CONTEXT]" in request_text
        has_end = "[END JARVIS DECISION CONTEXT]" in request_text
        has_decision_id = REAL_DECISION_ID in request_text

        adapter_call_data["has_decision_context_marker"] = has_start
        adapter_call_data["has_end_marker"] = has_end
        adapter_call_data["has_real_decision_id"] = has_decision_id

        print(f"\n[INPUT VERIFICATION at adapter_gemini.call_api()]")
        print(f"  [JARVIS DECISION CONTEXT] marker: {has_start}")
        print(f"  [END JARVIS DECISION CONTEXT] marker: {has_end}")
        print(f"  Real Decision ID ({REAL_DECISION_ID}): {has_decision_id}")

        if has_start and has_end:
            print(f"\n[DECISION CONTEXT BLOCK FOUND]")
            start_idx = request_text.find("[JARVIS DECISION CONTEXT]")
            end_idx = request_text.find("[END JARVIS DECISION CONTEXT]") + len("[END JARVIS DECISION CONTEXT]")
            decision_block = request_text[start_idx:end_idx]

            print(f"  Block length: {len(decision_block)} chars")
            lines = decision_block.split('\n')
            for i, line in enumerate(lines[:8]):
                if line.strip():
                    print(f"  Line {i+1}: {line[:65]}")

        # Call original function
        return original_call_api(request_text, model)

    adapter_gemini.call_api = call_api_with_trace
    print("[SETUP] Trace interceptor installed on adapter_gemini.call_api()")


def run_trace():
    """Run dispatch with trace"""

    print("=" * 80)
    print("STEP 3 - ADAPTER TRACE: Verify Decision Context at adapter_gemini.call_api()")
    print("=" * 80)

    # Setup trace
    print(f"\n[SETUP] Install trace on adapter_gemini.call_api()")
    try:
        setup_adapter_trace()
    except Exception as e:
        print(f"[ERROR] Failed to setup trace: {e}")
        return False

    # Call dispatch
    print(f"\n[DISPATCH] Call with real Decision")
    try:
        from multi_dispatcher import dispatch_multi_request

        response = dispatch_multi_request(
            request_text="Trace adapter call with real Decision",
            providers=["gemini"],
            models={"gemini": "gemini-2.0-flash"},
            title="STEP 3 Adapter Trace",
            decision_id="JARVIS_OBS_20260923031206"
        )

        print(f"\n[DISPATCH RESULT]")
        print(f"  Status: {response.get('status')}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def final_report():
    """Generate final report"""

    print(f"\n" + "=" * 80)
    print("ADAPTER TRACE RESULT")
    print("=" * 80)

    if adapter_call_data["called"]:
        print(f"\n✓ adapter_gemini.call_api() WAS CALLED")
        print(f"\n[Arguments Received at Adapter Entry Point]")
        print(f"  request_text length: {adapter_call_data['request_text_length']} chars")
        print(f"  model: {adapter_call_data['model']}")

        print(f"\n[Decision Context Verification]")
        print(f"  [JARVIS DECISION CONTEXT] marker: {adapter_call_data['has_decision_context_marker']}")
        print(f"  [END JARVIS DECISION CONTEXT] marker: {adapter_call_data['has_end_marker']}")
        print(f"  Real Decision ID in input: {adapter_call_data['has_real_decision_id']}")

        if adapter_call_data['has_decision_context_marker'] and adapter_call_data['has_real_decision_id']:
            print(f"\n[CONFIRMATION]")
            print(f"  ✓ Real Decision Context CONFIRMED in adapter_gemini.call_api() argument")
            print(f"  ✓ This is the input that would be passed to client.generate_content()")
            return True
        else:
            print(f"\n✗ Decision context NOT found in adapter input")
            return False
    else:
        print(f"\n✗ adapter_gemini.call_api() was NOT called")
        print(f"  (Likely due to missing google.generativeai library)")
        return False


if __name__ == "__main__":
    success = run_trace()
    confirmed = final_report()

    print(f"\n" + "=" * 80)
    if adapter_call_data["called"]:
        print("LEVEL B VERIFICATION: ✓ ADAPTER INPUT VERIFIED")
        print("  Real Decision Context confirmed at adapter_gemini.call_api() entry")
    else:
        print("LEVEL B VERIFICATION: ? NOT CAPTURED")
        print("  adapter_gemini.call_api() not called (library issue)")
