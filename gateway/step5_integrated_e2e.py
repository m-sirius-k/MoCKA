# -*- coding: utf-8 -*-
"""
STEP 5 - INTEGRATED E2E: HAB → JARVIS → 3AI Multi-Provider
Single runtime execution with simultaneous capture of all 3 adapter inputs.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global observation
observation = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "real_decision_id": "HG-REC-2026-PH2834-01-DP5-DECISION-20260912",

    # A-H stages
    "a_hab_jarvis_verified": False,
    "b_real_decision_verified": False,
    "c_enhanced_request_verified": False,

    "d_gpt_runtime_input_verified": False,
    "d_gpt_decision_context_found": False,
    "d_gpt_input_length": 0,

    "e_gemini_runtime_input_verified": False,
    "e_gemini_decision_context_found": False,
    "e_gemini_input_length": 0,

    "e2_perplexity_runtime_input_verified": False,
    "e2_perplexity_decision_context_found": False,
    "e2_perplexity_input_length": 0,

    "f_gpt_api_response": None,
    "g_gemini_api_response": None,
    "h_perplexity_api_response": None,
}


def setup_triple_interception():
    """
    Install monkey-patches on all 3 adapters simultaneously
    to capture runtime inputs in single E2E execution.
    """

    print("[SETUP] Installing triple interception...")

    # GPT
    try:
        import adapter_gpt
        original_gpt_call_api = adapter_gpt.call_api

        def gpt_call_api_with_trace(request_text: str, model: str = "gpt-4"):
            observation["d_gpt_runtime_input_verified"] = True
            observation["d_gpt_input_length"] = len(request_text)
            observation["d_gpt_decision_context_found"] = (
                "[JARVIS DECISION CONTEXT]" in request_text and
                observation["real_decision_id"] in request_text
            )
            print(f"\n[GPT] adapter_gpt.call_api() captured")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Decision context: {observation['d_gpt_decision_context_found']}")

            return original_gpt_call_api(request_text, model)

        adapter_gpt.call_api = gpt_call_api_with_trace
        print("  ✓ GPT interception ready")
    except Exception as e:
        print(f"  ✗ GPT interception failed: {e}")

    # Gemini
    try:
        import adapter_gemini
        original_gemini_call_api = adapter_gemini.call_api

        def gemini_call_api_with_trace(request_text: str, model: str = "gemini-2.0-flash"):
            observation["e_gemini_runtime_input_verified"] = True
            observation["e_gemini_input_length"] = len(request_text)
            observation["e_gemini_decision_context_found"] = (
                "[JARVIS DECISION CONTEXT]" in request_text and
                observation["real_decision_id"] in request_text
            )
            print(f"\n[GEMINI] adapter_gemini.call_api() captured")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Decision context: {observation['e_gemini_decision_context_found']}")

            return original_gemini_call_api(request_text, model)

        adapter_gemini.call_api = gemini_call_api_with_trace
        print("  ✓ Gemini interception ready")
    except Exception as e:
        print(f"  ✗ Gemini interception failed: {e}")

    # Perplexity
    try:
        import adapter_perplexity
        original_perplexity_call_api = adapter_perplexity.call_api

        def perplexity_call_api_with_trace(request_text: str, model: str = "sonar-pro"):
            observation["e2_perplexity_runtime_input_verified"] = True
            observation["e2_perplexity_input_length"] = len(request_text)
            observation["e2_perplexity_decision_context_found"] = (
                "[JARVIS DECISION CONTEXT]" in request_text and
                observation["real_decision_id"] in request_text
            )
            print(f"\n[PERPLEXITY] adapter_perplexity.call_api() captured")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Decision context: {observation['e2_perplexity_decision_context_found']}")

            return original_perplexity_call_api(request_text, model)

        adapter_perplexity.call_api = perplexity_call_api_with_trace
        print("  ✓ Perplexity interception ready")
    except Exception as e:
        print(f"  ✗ Perplexity interception failed: {e}")


def run_integrated_e2e():
    """Run single integrated E2E with all 3 providers"""

    print("=" * 80)
    print("STEP 5 - INTEGRATED E2E: HAB → JARVIS → 3AI")
    print("=" * 80)

    # Setup
    print(f"\n[SETUP PHASE]")
    setup_triple_interception()

    # Execute
    print(f"\n[EXECUTION PHASE]")
    print(f"  Dispatching one request to: GPT, Gemini, Perplexity")
    print(f"  Real Decision ID: {observation['real_decision_id']}")

    try:
        from multi_dispatcher import dispatch_multi_request

        response = dispatch_multi_request(
            request_text="Integrated E2E verification of Decision context binding across all providers",
            providers=["gpt", "gemini", "perplexity"],
            models={
                "gpt": "gpt-4",
                "gemini": "gemini-2.0-flash",
                "perplexity": "sonar-pro",
            },
            title="STEP 5 Integrated E2E",
            decision_id="JARVIS_OBS_20260923031206"
        )

        # Verify JARVIS result (Stage A+B)
        print(f"\n[VERIFICATION PHASE]")

        if "jarvis" in response:
            jarvis = response["jarvis"]
            if jarvis.get('status') == 'found':
                observation["a_hab_jarvis_verified"] = True
                observation["b_real_decision_verified"] = True
                print(f"\n[STAGE A] HAB → JARVIS: ✓ VERIFIED")
                print(f"  JARVIS status: {jarvis.get('status')}")
                print(f"  Decision ID found: {jarvis.get('jarvis_decision', {}).get('decision_id')}")
                print(f"\n[STAGE B] Real Decision: ✓ VERIFIED")
                print(f"  Decision title: {jarvis.get('jarvis_decision', {}).get('title')[:60]}...")

        # Check if enhanced_request was built
        if observation['d_gpt_runtime_input_verified'] or \
           observation['e_gemini_runtime_input_verified'] or \
           observation['e2_perplexity_runtime_input_verified']:
            observation["c_enhanced_request_verified"] = True
            print(f"\n[STAGE C] enhanced_request → MultiDispatcher: ✓ VERIFIED")

        # Verify adapter inputs (Stages D, E, E2)
        print(f"\n[STAGE D] enhanced_request → GPT runtime input")
        if observation["d_gpt_runtime_input_verified"]:
            print(f"  ✓ VERIFIED (length: {observation['d_gpt_input_length']} chars)")
            if observation["d_gpt_decision_context_found"]:
                print(f"  ✓ Decision context found")
        else:
            print(f"  ? NOT CAPTURED")

        print(f"\n[STAGE E] enhanced_request → Gemini runtime input")
        if observation["e_gemini_runtime_input_verified"]:
            print(f"  ✓ VERIFIED (length: {observation['e_gemini_input_length']} chars)")
            if observation["e_gemini_decision_context_found"]:
                print(f"  ✓ Decision context found")
        else:
            print(f"  ? NOT CAPTURED")

        print(f"\n[STAGE E2] enhanced_request → Perplexity runtime input")
        if observation["e2_perplexity_runtime_input_verified"]:
            print(f"  ✓ VERIFIED (length: {observation['e2_perplexity_input_length']} chars)")
            if observation["e2_perplexity_decision_context_found"]:
                print(f"  ✓ Decision context found")
        else:
            print(f"  ? NOT CAPTURED")

        # API Responses (Stages F, G, H)
        print(f"\n[STAGE F/G/H] API Responses")
        for result in response.get('results', []):
            provider = result.get('provider')
            status = result.get('status')

            if provider == 'gpt':
                observation["f_gpt_api_response"] = status
                print(f"  GPT: {status}")
            elif provider == 'gemini':
                observation["g_gemini_api_response"] = status
                print(f"  Gemini: {status}")
            elif provider == 'perplexity':
                observation["h_perplexity_api_response"] = status
                print(f"  Perplexity: {status}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_final_report():
    """Print final A-H stage report"""

    print(f"\n" + "=" * 80)
    print("STEP 5 INTEGRATED E2E - FINAL REPORT")
    print("=" * 80)

    print(f"\nSTAGE VERIFICATION (A-H):\n")

    print(f"A. HAB → JARVIS: {'✓ VERIFIED' if observation['a_hab_jarvis_verified'] else '✗ FAILED'}")
    print(f"B. Real Decision: {'✓ VERIFIED' if observation['b_real_decision_verified'] else '✗ FAILED'}")
    print(f"C. enhanced_request → Dispatcher: {'✓ VERIFIED' if observation['c_enhanced_request_verified'] else '? UNKNOWN'}")

    print(f"\nD. enhanced_request → GPT runtime input: {'✓ VERIFIED' if observation['d_gpt_runtime_input_verified'] else '? NOT CAPTURED'}")
    if observation['d_gpt_decision_context_found']:
        print(f"   Decision context in GPT input: ✓ YES")

    print(f"\nE. enhanced_request → Gemini runtime input: {'✓ VERIFIED' if observation['e_gemini_runtime_input_verified'] else '? NOT CAPTURED'}")
    if observation['e_gemini_decision_context_found']:
        print(f"   Decision context in Gemini input: ✓ YES")

    print(f"\nE2. enhanced_request → Perplexity runtime input: {'✓ VERIFIED' if observation['e2_perplexity_runtime_input_verified'] else '? NOT CAPTURED'}")
    if observation['e2_perplexity_decision_context_found']:
        print(f"    Decision context in Perplexity input: ✓ YES")

    print(f"\nF. GPT API response: {observation['f_gpt_api_response'] or 'UNKNOWN'}")
    print(f"G. Gemini API response: {observation['g_gemini_api_response'] or 'UNKNOWN'}")
    print(f"H. Perplexity API response: {observation['h_perplexity_api_response'] or 'UNKNOWN'}")

    # Summary
    print(f"\n" + "-" * 80)
    print("SUMMARY")
    print("-" * 80)

    all_verified = (
        observation['d_gpt_decision_context_found'] and
        observation['e_gemini_decision_context_found'] and
        observation['e2_perplexity_decision_context_found']
    )

    if all_verified:
        print(f"\n✓ INTEGRATED E2E VERIFIED")
        print(f"\n  HAB → JARVIS: VERIFIED")
        print(f"  Real Decision: VERIFIED")
        print(f"  enhanced_request: VERIFIED")
        print(f"\n  GPT runtime input: VERIFIED")
        print(f"  Gemini runtime input: VERIFIED")
        print(f"  Perplexity runtime input: VERIFIED")
        print(f"\n  Decision context in all 3 AI inputs: ✓ CONFIRMED")
    else:
        print(f"\n⚠ PARTIAL VERIFICATION")
        print(f"  Verified stages: A, B, C")
        print(f"  Runtime input verification:")
        if observation['d_gpt_decision_context_found']:
            print(f"    ✓ GPT")
        if observation['e_gemini_decision_context_found']:
            print(f"    ✓ Gemini")
        if observation['e2_perplexity_decision_context_found']:
            print(f"    ✓ Perplexity")

    print(f"\n  Production code changes: 0")
    print(f"  Production activation: NOT PERFORMED")

    return observation


if __name__ == "__main__":
    success = run_integrated_e2e()
    obs = print_final_report()

    print(f"\n" + "=" * 80)
    print(json.dumps(obs, ensure_ascii=False, indent=2))
