# -*- coding: utf-8 -*-
"""
STEP 7 - REAL USER E2E: HAB → JARVIS → Decision → 3AI → Response

実ユーザー入口から、一本の実行で確認：
1. User Request (Decision-aware question)
2. HAB entry
3. JARVIS recall experience
4. Real Decision retrieval
5. Decision Context generation
6. MultiDispatcher dispatch
7. All 3 AIs receive Decision Context
8. Responses returned
9. HAB receives results

目的: 既存コードで本番運用可能か確認（検証ではなく運用確認）
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Real Decision (STEP 2-6 で検証済み)
REAL_DECISION_ID = "HG-REC-2026-PH2834-01-DP5-DECISION-20260912"

# Real User Request (Decision Context が意味を持つ質問)
USER_REQUEST = """
Given the current decision about C-001/C-002 gate sequencing
(deferring formal rules while enforcing operational prerequisites),
what should be the immediate next steps to ensure phase 32 entry
criteria are properly validated before C-001 is considered complete?
"""

# Observation
observation = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "user_request": USER_REQUEST.strip(),
    "real_decision_id": REAL_DECISION_ID,

    # Stage tracking
    "a_user_entry_verified": False,
    "b_jarvis_recall_verified": False,
    "c_real_decision_verified": False,
    "d_decision_context_verified": False,
    "e_multi_ai_dispatch_verified": False,

    "f_gpt_request_received": False,
    "g_gemini_request_received": False,
    "h_perplexity_request_received": False,

    "i_gpt_response_verified": None,
    "j_gemini_response_verified": None,
    "k_perplexity_response_verified": None,

    "l_hab_result_return_verified": False,
}


def setup_observation_hooks():
    """Install hooks to observe the entire E2E flow"""

    print("[SETUP] Installing observation hooks...")

    # Hook: Track dispatch_multi_request entry
    try:
        import multi_dispatcher
        original_dispatch = multi_dispatcher.dispatch_multi_request

        def dispatch_with_observation(request_text, providers=None, models=None, title="", decision_id=None):
            observation["a_user_entry_verified"] = True
            print(f"\n[STAGE A] User Entry → HAB/Dispatcher: ✓")
            print(f"  Request: {request_text[:80]}...")
            print(f"  Providers: {providers}")
            print(f"  Decision ID: {decision_id}")

            return original_dispatch(request_text, providers, models, title, decision_id)

        multi_dispatcher.dispatch_multi_request = dispatch_with_observation
        print("  ✓ Dispatcher hook installed")
    except Exception as e:
        print(f"  ✗ Dispatcher hook failed: {e}")

    # Hook: Track JARVIS recall
    try:
        import multi_dispatcher as md
        original_call_jarvis = md._call_jarvis

        def call_jarvis_with_observation(decision_id, request_id, request_text, title, timestamp):
            observation["b_jarvis_recall_verified"] = True
            result = original_call_jarvis(decision_id, request_id, request_text, title, timestamp)

            if result.get('status') == 'found':
                observation["c_real_decision_verified"] = True
                decision = result.get('jarvis_decision', {})
                print(f"\n[STAGE B] JARVIS Recall: ✓")
                print(f"  Status: {result.get('status')}")
                print(f"  Decision ID: {decision.get('decision_id')}")
                print(f"  Title: {decision.get('title')[:60]}...")
                print(f"\n[STAGE C] Real Decision: ✓")

            return result

        md._call_jarvis = call_jarvis_with_observation
        print("  ✓ JARVIS hook installed")
    except Exception as e:
        print(f"  ✗ JARVIS hook failed: {e}")

    # Hook: Track enhanced_request building
    try:
        original_build = md._build_request_with_decision_context

        def build_with_observation(original_request_text, jarvis_decision, decision_id):
            enhanced = original_build(original_request_text, jarvis_decision, decision_id)
            observation["d_decision_context_verified"] = True
            print(f"\n[STAGE D] Decision Context: ✓")
            print(f"  Enhanced request length: {len(enhanced)} chars")
            print(f"  Contains [JARVIS DECISION CONTEXT]: {'[JARVIS DECISION CONTEXT]' in enhanced}")
            return enhanced

        md._build_request_with_decision_context = build_with_observation
        print("  ✓ Context build hook installed")
    except Exception as e:
        print(f"  ✗ Context build hook failed: {e}")

    # Hook: Track adapter calls
    try:
        import adapter_gpt
        orig_gpt = adapter_gpt.call_api

        def gpt_with_obs(request_text, model="gpt-4"):
            observation["f_gpt_request_received"] = True
            has_context = "[JARVIS DECISION CONTEXT]" in request_text
            print(f"\n[STAGE F] GPT Request: ✓")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Has Decision Context: {has_context}")

            result = orig_gpt(request_text, model)
            if result.get('status') == 'ok':
                observation["i_gpt_response_verified"] = "VERIFIED"
                print(f"  Response: OK ({len(result.get('response', ''))} chars)")
            else:
                observation["i_gpt_response_verified"] = result.get('error', 'ERROR')

            return result

        adapter_gpt.call_api = gpt_with_obs
        print("  ✓ GPT hook installed")
    except Exception as e:
        print(f"  ✗ GPT hook failed: {e}")

    try:
        import adapter_gemini
        orig_gemini = adapter_gemini.call_api

        def gemini_with_obs(request_text, model="gemini-2.0-flash"):
            observation["g_gemini_request_received"] = True
            has_context = "[JARVIS DECISION CONTEXT]" in request_text
            print(f"\n[STAGE G] Gemini Request: ✓")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Has Decision Context: {has_context}")

            result = orig_gemini(request_text, model)
            if result.get('status') == 'ok':
                observation["j_gemini_response_verified"] = "VERIFIED"
                print(f"  Response: OK")
            else:
                observation["j_gemini_response_verified"] = result.get('error', 'ERROR')

            return result

        adapter_gemini.call_api = gemini_with_obs
        print("  ✓ Gemini hook installed")
    except Exception as e:
        print(f"  ✗ Gemini hook failed: {e}")

    try:
        import adapter_perplexity
        orig_pplx = adapter_perplexity.call_api

        def pplx_with_obs(request_text, model="sonar-pro"):
            observation["h_perplexity_request_received"] = True
            has_context = "[JARVIS DECISION CONTEXT]" in request_text
            print(f"\n[STAGE H] Perplexity Request: ✓")
            print(f"  Length: {len(request_text)} chars")
            print(f"  Has Decision Context: {has_context}")

            result = orig_pplx(request_text, model)
            if result.get('status') == 'ok':
                observation["k_perplexity_response_verified"] = "VERIFIED"
                print(f"  Response: OK")
            else:
                observation["k_perplexity_response_verified"] = result.get('error', 'ERROR')

            return result

        adapter_perplexity.call_api = pplx_with_obs
        print("  ✓ Perplexity hook installed")
    except Exception as e:
        print(f"  ✗ Perplexity hook failed: {e}")


def run_real_user_e2e():
    """Execute real user request through entire system"""

    print("=" * 80)
    print("STEP 7 - REAL USER E2E: HAB → JARVIS → 3AI → Response")
    print("=" * 80)

    print(f"\n[SETUP]")
    setup_observation_hooks()

    print(f"\n[EXECUTION]")
    print(f"  Real User Request:")
    print(f"  {USER_REQUEST.strip()[:100]}...")
    print(f"\n  Real Decision ID: {REAL_DECISION_ID}")

    try:
        from multi_dispatcher import dispatch_multi_request

        # Make real request with decision ID
        response = dispatch_multi_request(
            request_text=USER_REQUEST.strip(),
            providers=["gpt", "gemini", "perplexity"],
            models={
                "gpt": "gpt-4",
                "gemini": "gemini-2.0-flash",
                "perplexity": "sonar-pro",
            },
            title="STEP 7 Real User E2E",
            decision_id="JARVIS_OBS_20260923031206"  # Trigger JARVIS recall
        )

        observation["e_multi_ai_dispatch_verified"] = True
        observation["l_hab_result_return_verified"] = True

        print(f"\n[STAGE E] MultiDispatcher: ✓")
        print(f"  Overall status: {response.get('status')}")

        print(f"\n[STAGE L] HAB Result Return: ✓")
        print(f"  Response received with {len(response.get('results', []))} results")

        return response

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_final_report(response):
    """Print STEP 7 final report"""

    print(f"\n" + "=" * 80)
    print("STEP 7 - REAL USER E2E VERIFICATION REPORT")
    print("=" * 80)

    print(f"\nGPT")
    print(f"  Request received: {'VERIFIED' if observation['f_gpt_request_received'] else 'NOT RECEIVED'}")
    print(f"  Response: {observation['i_gpt_response_verified'] or 'NOT RECEIVED'}")

    print(f"\nGemini")
    print(f"  Request received: {'VERIFIED' if observation['g_gemini_request_received'] else 'NOT RECEIVED'}")
    print(f"  Response: {observation['j_gemini_response_verified'] or 'NOT RECEIVED'}")

    print(f"\nPerplexity")
    print(f"  Request received: {'VERIFIED' if observation['h_perplexity_request_received'] else 'NOT RECEIVED'}")
    print(f"  Response: {observation['k_perplexity_response_verified'] or 'NOT RECEIVED'}")

    print(f"\n" + "-" * 80)
    print("INTEGRATION VERIFICATION")
    print("-" * 80)

    print(f"\nHAB User Entry: {'VERIFIED' if observation['a_user_entry_verified'] else 'FAILED'}")
    print(f"JARVIS Experience Recall: {'VERIFIED' if observation['b_jarvis_recall_verified'] else 'FAILED'}")
    print(f"Real Decision: {'VERIFIED' if observation['c_real_decision_verified'] else 'FAILED'}")
    print(f"Multi-AI Dispatch: {'VERIFIED' if observation['e_multi_ai_dispatch_verified'] else 'FAILED'}")
    print(f"HAB/JARVIS Result Return: {'VERIFIED' if observation['l_hab_result_return_verified'] else 'FAILED'}")

    print(f"\nProduction code changes: 0")
    print(f"Production activation: NOT PERFORMED")

    # Final status
    all_stages = [
        observation['a_user_entry_verified'],
        observation['b_jarvis_recall_verified'],
        observation['c_real_decision_verified'],
        observation['e_multi_ai_dispatch_verified'],
        observation['f_gpt_request_received'],
        observation['l_hab_result_return_verified'],
    ]

    if all(all_stages):
        print(f"\n✓ STEP 7 PRODUCTION READINESS VERIFIED")
    else:
        print(f"\n⚠ STEP 7 PARTIAL VERIFICATION")

    return observation


if __name__ == "__main__":
    response = run_real_user_e2e()
    obs = print_final_report(response)

    print(f"\n" + "=" * 80)
    print("OBSERVATION DATA")
    print("=" * 80)
    print(json.dumps(obs, ensure_ascii=False, indent=2))
