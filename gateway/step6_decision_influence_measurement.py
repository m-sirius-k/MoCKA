# -*- coding: utf-8 -*-
"""
STEP 6 - DECISION CONTEXT INFLUENCE MEASUREMENT

Purpose: Measure whether Decision Context actually influences AI output.
Not just delivery, but actual impact on response content.

Comparison Method:
  Condition A: Request WITHOUT Decision Context
  Condition B: Request WITH Decision Context (Real Decision from STEP 5)

Same user request, same AI, same model, fixed parameters.
Compare actual outputs.

Real Decision ID: HG-REC-2026-PH2834-01-DP5-DECISION-20260912
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Real Decision Context for Condition B
REAL_DECISION_CONTEXT = """[JARVIS DECISION CONTEXT]
Decision ID: HG-REC-2026-PH2834-01-DP5-DECISION-20260912
Title: DP-5: C-001/C-002 Gate Sequencing and Dependency
Decision: Candidate D-oriented pragmatic C: Defer formal sequencing rule pending C-001/C-002 satisfaction criteria definition; operationally enforce strict sequential (C-001 prerequisite to Phase 32 entry)
Rationale: C-001/C-002 satisfaction criteria not yet explicit. Cannot determine logical sequencing without understanding what each gate requires. Operational sequencing (C-001→C-002) enforced as pragmatic default pending formal criteria definition. Formal governance rule deferred to next revision cycle.
Approved By: Human Gate Review Panel (HG-REC-2026-PH2834-01-REF-01)
Approved At: 2026-09-12T06:30:18Z
[END JARVIS DECISION CONTEXT]
"""

# User Request (fixed)
USER_REQUEST = "What are the key considerations for gate sequencing in a phased rollout plan?"

# Observation
observation = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "user_request": USER_REQUEST,

    # GPT - Condition A (WITHOUT Decision Context)
    "gpt_condition_a_input": None,
    "gpt_condition_a_input_length": 0,
    "gpt_condition_a_response": None,
    "gpt_condition_a_response_length": 0,
    "gpt_condition_a_verified": False,

    # GPT - Condition B (WITH Decision Context)
    "gpt_condition_b_input": None,
    "gpt_condition_b_input_length": 0,
    "gpt_condition_b_response": None,
    "gpt_condition_b_response_length": 0,
    "gpt_condition_b_verified": False,
    "gpt_condition_b_has_decision_context": False,

    # Comparison
    "gpt_output_difference_observed": None,
    "gpt_decision_influence": None,

    # Status
    "gpt_api_available": False,
    "gemini_tested": False,
    "perplexity_tested": False,
}


def intercept_gpt_responses():
    """Install interception on adapter_gpt to capture inputs and outputs"""
    try:
        import adapter_gpt

        original_call_api = adapter_gpt.call_api

        call_count = 0

        def call_api_with_capture(request_text: str, model: str = "gpt-4"):
            nonlocal call_count
            call_count += 1

            # Capture input
            has_decision_context = "[JARVIS DECISION CONTEXT]" in request_text

            # Call original
            result = original_call_api(request_text, model)

            # Capture result
            if call_count == 1:  # Condition A
                observation["gpt_condition_a_input"] = request_text[:100] + "..." if len(request_text) > 100 else request_text
                observation["gpt_condition_a_input_length"] = len(request_text)
                observation["gpt_condition_a_response"] = result.get("response", "")[:200] if result.get("response") else ""
                observation["gpt_condition_a_response_length"] = len(result.get("response", ""))
                observation["gpt_condition_a_verified"] = True

                print(f"\n[GPT CONDITION A - WITHOUT Decision Context]")
                print(f"  Input length: {observation['gpt_condition_a_input_length']} chars")
                print(f"  Has Decision Context: False")
                print(f"  Response length: {observation['gpt_condition_a_response_length']} chars")

            elif call_count == 2:  # Condition B
                observation["gpt_condition_b_input"] = request_text[:100] + "..." if len(request_text) > 100 else request_text
                observation["gpt_condition_b_input_length"] = len(request_text)
                observation["gpt_condition_b_has_decision_context"] = has_decision_context
                observation["gpt_condition_b_response"] = result.get("response", "")[:200] if result.get("response") else ""
                observation["gpt_condition_b_response_length"] = len(result.get("response", ""))
                observation["gpt_condition_b_verified"] = True

                print(f"\n[GPT CONDITION B - WITH Decision Context]")
                print(f"  Input length: {observation['gpt_condition_b_input_length']} chars")
                print(f"  Has Decision Context: {has_decision_context}")
                print(f"  Response length: {observation['gpt_condition_b_response_length']} chars")

            return result

        adapter_gpt.call_api = call_api_with_capture
        observation["gpt_api_available"] = True
        print("[SETUP] GPT interception installed")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to setup GPT interception: {e}")
        return False


def run_gpt_comparison():
    """Run GPT comparison: Condition A vs B"""

    print("=" * 80)
    print("STEP 6 - DECISION INFLUENCE MEASUREMENT")
    print("=" * 80)

    # Setup
    print(f"\n[SETUP] Install GPT interception")
    setup_ok = intercept_gpt_responses()

    if not setup_ok:
        print("[ERROR] Failed to setup interception")
        return False

    # Execute Condition A (WITHOUT Decision Context)
    print(f"\n[CONDITION A] WITHOUT Decision Context")
    print(f"  Request: {USER_REQUEST}")

    try:
        from adapter_gpt import call_api as gpt_call_api_direct

        result_a = gpt_call_api_direct(USER_REQUEST, "gpt-4")

        if result_a.get("status") == "ok":
            print(f"  Status: OK")
        else:
            print(f"  Status: ERROR - {result_a.get('error')}")
            return False

    except Exception as e:
        print(f"  [ERROR] Condition A failed: {e}")
        return False

    # Execute Condition B (WITH Decision Context)
    print(f"\n[CONDITION B] WITH Decision Context")

    request_with_context = f"{REAL_DECISION_CONTEXT}\n\nOriginal request:\n{USER_REQUEST}"
    print(f"  Request: [Decision Context] + Original request")

    try:
        result_b = gpt_call_api_direct(request_with_context, "gpt-4")

        if result_b.get("status") == "ok":
            print(f"  Status: OK")
        else:
            print(f"  Status: ERROR - {result_b.get('error')}")
            return False

    except Exception as e:
        print(f"  [ERROR] Condition B failed: {e}")
        return False

    return True


def analyze_outputs():
    """Analyze output differences"""

    print(f"\n[COMPARISON ANALYSIS]")

    if not (observation["gpt_condition_a_verified"] and observation["gpt_condition_b_verified"]):
        print(f"  Cannot compare - one or both conditions not completed")
        observation["gpt_decision_influence"] = "UNKNOWN"
        return

    response_a = observation["gpt_condition_a_response"]
    response_b = observation["gpt_condition_b_response"]

    # Check if responses are significantly different
    if response_a and response_b:
        # Simple comparison: check if responses contain different keywords

        # Check for decision-related keywords in Condition B
        decision_keywords = ["gate", "sequencing", "sequential", "C-001", "C-002", "prerequisite"]

        keywords_in_b = sum(1 for kw in decision_keywords if kw.lower() in response_b.lower())
        keywords_in_a = sum(1 for kw in decision_keywords if kw.lower() in response_a.lower())

        print(f"\n  Decision-related keywords:")
        print(f"    Condition A (WITHOUT): {keywords_in_a} keywords detected")
        print(f"    Condition B (WITH): {keywords_in_b} keywords detected")

        if response_a == response_b:
            print(f"\n  Responses: IDENTICAL")
            observation["gpt_output_difference_observed"] = False
        else:
            print(f"\n  Responses: DIFFERENT")
            observation["gpt_output_difference_observed"] = True

            # Check length difference
            len_diff = observation["gpt_condition_b_response_length"] - observation["gpt_condition_a_response_length"]
            if len_diff > 0:
                print(f"    Condition B is {len_diff} chars longer")
            elif len_diff < 0:
                print(f"    Condition B is {-len_diff} chars shorter")

        # Determine influence
        if keywords_in_b > keywords_in_a and observation["gpt_output_difference_observed"]:
            print(f"\n  [OBSERVATION] Decision Context response contains more decision-related keywords")
            observation["gpt_decision_influence"] = "OBSERVED"
        else:
            print(f"\n  [OBSERVATION] No clear influence pattern detected")
            observation["gpt_decision_influence"] = "UNKNOWN"
    else:
        observation["gpt_decision_influence"] = "UNKNOWN"


def print_final_report():
    """Print final report"""

    print(f"\n" + "=" * 80)
    print("STEP 6 - DECISION INFLUENCE MEASUREMENT REPORT")
    print("=" * 80)

    print(f"\nGPT")
    print(f"  WITHOUT input: {'VERIFIED' if observation['gpt_condition_a_verified'] else 'FAILED'}")
    print(f"  WITH input: {'VERIFIED' if observation['gpt_condition_b_verified'] else 'FAILED'}")

    if observation["gpt_condition_a_verified"]:
        print(f"  WITHOUT response: VERIFIED ({observation['gpt_condition_a_response_length']} chars)")
    else:
        print(f"  WITHOUT response: FAILED")

    if observation["gpt_condition_b_verified"]:
        print(f"  WITH response: VERIFIED ({observation['gpt_condition_b_response_length']} chars)")
    else:
        print(f"  WITH response: FAILED")

    if observation["gpt_output_difference_observed"] is not None:
        diff_status = "OBSERVED" if observation["gpt_output_difference_observed"] else "NOT OBSERVED"
        print(f"  Output difference: {diff_status}")

    if observation["gpt_decision_influence"]:
        print(f"  Decision influence: {observation['gpt_decision_influence']}")

    print(f"\nProduction code changes: 0")
    print(f"Production activation: NOT PERFORMED")

    return observation


if __name__ == "__main__":
    success = run_gpt_comparison()

    if success:
        analyze_outputs()

    obs = print_final_report()

    print(f"\n" + "=" * 80)
    print("DETAILED OBSERVATION DATA")
    print("=" * 80)
    print(json.dumps(obs, ensure_ascii=False, indent=2))
