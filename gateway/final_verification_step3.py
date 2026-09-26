# -*- coding: utf-8 -*-
"""
STEP 3 FINAL VERIFICATION - Runtime Interception & Gemini API Response

目的:
  1. client.generate_content() に渡される実引数をキャプチャ
  2. Gemini APIの実レスポンス確認
  3. A/B/Cの3段階判定

制約:
  - 既存コード変更禁止
  - 実行時のMonkey-patching only
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global observation store
final_observation = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "decision_id": None,
    "real_decision_id": "HG-REC-2026-PH2834-01-DP5-DECISION-20260912",
    "code_path_verified": False,
    "runtime_input_captured": False,
    "has_decision_context_marker": False,
    "has_end_marker": False,
    "decision_id_in_input": False,
    "captured_input": None,
    "captured_input_length": 0,
    "gemini_api_response": None,
    "gemini_api_status": None,
    "gemini_api_error": None,
}


def intercept_generate_content():
    """
    Monkey-patch genai.GenerativeModel.generate_content を実装
    実引数を完全にキャプチャ（変更なし）
    """
    try:
        import google.generativeai as genai

        original_init = genai.GenerativeModel.__init__
        original_generate = genai.GenerativeModel.generate_content

        def init_with_tracking(self, *args, **kwargs):
            """Track model initialization"""
            result = original_init(self, *args, **kwargs)
            return result

        def generate_content_interceptor(self, contents, **kwargs):
            """
            Intercept generate_content() call
            Capture actual arguments WITHOUT modification
            """

            # Capture input
            if isinstance(contents, str):
                input_text = contents
            else:
                input_text = str(contents)

            final_observation["captured_input"] = input_text
            final_observation["captured_input_length"] = len(input_text)
            final_observation["runtime_input_captured"] = True

            print(f"\n[RUNTIME INTERCEPTION] generate_content() called")
            print(f"  Input type: {type(contents).__name__}")
            print(f"  Input length: {len(input_text)} chars")

            # Check for Decision context markers
            has_decision_start = "[JARVIS DECISION CONTEXT]" in input_text
            has_decision_end = "[END JARVIS DECISION CONTEXT]" in input_text
            has_real_decision_id = final_observation["real_decision_id"] in input_text

            final_observation["has_decision_context_marker"] = has_decision_start
            final_observation["has_end_marker"] = has_decision_end
            final_observation["decision_id_in_input"] = has_real_decision_id

            print(f"\n[INPUT VERIFICATION]")
            print(f"  [JARVIS DECISION CONTEXT] marker: {has_decision_start}")
            print(f"  [END JARVIS DECISION CONTEXT] marker: {has_decision_end}")
            print(f"  Real Decision ID present: {has_real_decision_id}")

            if has_decision_start and has_decision_end:
                start_idx = input_text.find("[JARVIS DECISION CONTEXT]")
                end_idx = input_text.find("[END JARVIS DECISION CONTEXT]") + len("[END JARVIS DECISION CONTEXT]")
                decision_block = input_text[start_idx:end_idx]

                print(f"\n[DECISION CONTEXT BLOCK] ({len(decision_block)} chars)")
                lines = decision_block.split('\n')[:8]
                for line in lines:
                    if line.strip():
                        print(f"  {line[:70]}")

            print(f"\n[CALLING] Original generate_content()...")

            try:
                response = original_generate(self, contents, **kwargs)
                final_observation["gemini_api_status"] = "ok"
                final_observation["gemini_api_response"] = str(response.text)[:200] if hasattr(response, 'text') else str(response)[:200]

                print(f"  ✓ Gemini API returned response")
                return response

            except Exception as api_error:
                error_msg = str(api_error)
                final_observation["gemini_api_status"] = "error"
                final_observation["gemini_api_error"] = error_msg

                print(f"  ✗ Gemini API error: {error_msg}")
                raise

        genai.GenerativeModel.__init__ = init_with_tracking
        genai.GenerativeModel.generate_content = generate_content_interceptor

        print("[SETUP] Monkey-patch installed on genai.GenerativeModel")
        return True

    except ImportError as e:
        print(f"[ERROR] google.generativeai not available: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to setup interception: {e}")
        return False


def run_final_verification():
    """Run final verification"""

    print("=" * 80)
    print("STEP 3 FINAL VERIFICATION - Runtime Interception & Gemini API")
    print("=" * 80)

    # Step 1: Setup interception
    print(f"\n[STEP 1] Setup Runtime Interception")
    interception_ready = intercept_generate_content()

    if not interception_ready:
        print("[WARNING] Interception setup failed - API library may not be available")

    # Step 2: Call dispatch with real decision
    print(f"\n[STEP 2] Call dispatch_multi_request with real Decision")
    print(f"  Real Decision ID: {final_observation['real_decision_id']}")
    print(f"  Provider: gemini only")

    try:
        from multi_dispatcher import dispatch_multi_request

        response = dispatch_multi_request(
            request_text="Final verification of decision context binding",
            providers=["gemini"],
            models={"gemini": "gemini-2.0-flash"},
            title="STEP 3 Final Verification",
            decision_id="JARVIS_OBS_20260923031206"
        )

        # Step 3: Check dispatch result
        print(f"\n[STEP 3] Dispatch Result")
        print(f"  Overall status: {response.get('status')}")

        # Check JARVIS result
        if "jarvis" in response:
            jarvis = response["jarvis"]
            print(f"\n[JARVIS RESULT]")
            print(f"  Status: {jarvis.get('status')}")
            if jarvis.get('jarvis_decision'):
                decision = jarvis.get('jarvis_decision')
                final_observation["decision_id"] = decision.get('decision_id')
                print(f"  Decision ID: {decision.get('decision_id')}")
                final_observation["code_path_verified"] = True

        # Check Gemini result
        print(f"\n[GEMINI RESULT]")
        for result in response.get('results', []):
            if result.get('provider') == 'gemini':
                status = result.get('status')
                print(f"  Status: {status}")

                if status == 'ok':
                    print(f"  ✓ Gemini API returned OK")
                    response_preview = result.get('response', '')[:100]
                    print(f"  Response: {response_preview}...")
                elif status == 'error':
                    error = result.get('error', '')
                    print(f"  Error: {error}")

                    # Distinguish between missing library and API error
                    if 'google.generativeai' in error or 'No module' in error:
                        print(f"  [Note] Missing google.generativeai library")
                        final_observation["gemini_api_status"] = "library_missing"

        return True

    except Exception as e:
        print(f"\n[ERROR] Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_final_verdict():
    """Print final 3-level verification verdict"""

    print(f"\n" + "=" * 80)
    print("FINAL VERIFICATION VERDICT")
    print("=" * 80)

    # Level A: CODE PATH VERIFIED
    print(f"\n[LEVEL A] CODE PATH VERIFIED")
    if final_observation["code_path_verified"] and final_observation["decision_id"]:
        print(f"  ✓ YES")
        print(f"  JARVIS decision found and passed to provider loop")
        print(f"  Decision ID: {final_observation['decision_id']}")
    else:
        print(f"  ✗ INCOMPLETE")

    # Level B: RUNTIME INPUT VERIFIED
    print(f"\n[LEVEL B] RUNTIME INPUT VERIFIED")
    if final_observation["runtime_input_captured"]:
        print(f"  ✓ YES - generate_content() called and arguments captured")
        print(f"  Input length: {final_observation['captured_input_length']} chars")
        print(f"  Decision context block: {final_observation['has_decision_context_marker'] and final_observation['has_end_marker']}")
        print(f"  Real Decision ID in input: {final_observation['decision_id_in_input']}")

        if final_observation['has_decision_context_marker'] and final_observation['decision_id_in_input']:
            print(f"\n  [CONFIRMATION]")
            print(f"    {final_observation['real_decision_id']} is in generate_content() argument")
            print(f"    [JARVIS DECISION CONTEXT] marker present")
    else:
        print(f"  ? NOT CAPTURED")
        if final_observation["gemini_api_status"] == "library_missing":
            print(f"  (google.generativeai library not available for interception)")
        else:
            print(f"  (generate_content() may not have been called)")

    # Level C: GEMINI API RESPONSE VERIFIED
    print(f"\n[LEVEL C] GEMINI API RESPONSE VERIFIED")
    api_status = final_observation.get("gemini_api_status")

    if api_status == "ok":
        print(f"  ✓ YES - Gemini API returned response")
        response = final_observation.get("gemini_api_response", "")[:100]
        print(f"  Response: {response}...")
    elif api_status == "error":
        error = final_observation.get("gemini_api_error", "Unknown")
        print(f"  ✗ NO - Gemini API returned error")
        print(f"  Error: {error}")
    elif api_status == "library_missing":
        print(f"  ? UNABLE - google.generativeai not installed")
        print(f"  (Cannot verify API call, but code path is confirmed)")
    else:
        print(f"  ? UNKNOWN - API not reached")

    # Final Classification
    print(f"\n" + "-" * 80)
    print("FINAL CLASSIFICATION")
    print("-" * 80)

    a_ok = final_observation.get("code_path_verified", False)
    b_ok = final_observation.get("runtime_input_captured", False) and \
           final_observation.get("has_decision_context_marker", False) and \
           final_observation.get("decision_id_in_input", False)
    c_ok = final_observation.get("gemini_api_status") == "ok"

    print(f"\nA (Code Path): {['✗', '✓'][a_ok]}")
    print(f"B (Runtime Input): {['?', '✓'][b_ok]}")
    print(f"C (API Response): {['?', '✓'][c_ok]}")

    if a_ok and b_ok and c_ok:
        print(f"\n✓✓✓ GEMINI REAL E2E VERIFIED (A+B+C)")
    elif a_ok and b_ok:
        print(f"\n✓✓ Gemini Decision Context Binding VERIFIED (A+B)")
    elif a_ok:
        print(f"\n✓ Code path verified, but input/response not observable")
    else:
        print(f"\n✗ Verification incomplete")

    return final_observation


if __name__ == "__main__":
    success = run_final_verification()
    observation = print_final_verdict()

    # Save observation
    print(f"\n" + "=" * 80)
    print("OBSERVATION DATA")
    print("=" * 80)
    print(json.dumps(observation, ensure_ascii=False, indent=2))
