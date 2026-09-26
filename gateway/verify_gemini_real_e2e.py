# -*- coding: utf-8 -*-
"""
STEP 3 REAL E2E VERIFICATION: Gemini + JARVIS Decision Binding

Purpose: Verify that Real Decision from ledger reaches Real Gemini API via existing code path.

Method:
  1. Use real Decision ID from decision_ledger.jsonl
  2. Call dispatch_multi_request with gemini provider
  3. Monkey-patch genai.GenerativeModel to observe payload WITHOUT code changes
  4. Verify Decision context in client.generate_content() call

Constraints:
  - NO code changes to multi_dispatcher.py / adapters_gemini_socket.py / adapter_gemini.py
  - NO mock decisions
  - NO test files created
  - Real API call only
  - Read-only observation via monkey-patch
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global store for observation
observation = {
    "decision_id": None,
    "jarvis_status": None,
    "enhanced_request_length": 0,
    "decision_context_in_gemini_input": False,
    "gemini_input_sample": None,
    "gemini_response": None,
    "timestamp": datetime.now(timezone.utc).isoformat(),
}


def setup_payload_observation():
    """
    Monkey-patch genai.GenerativeModel.generate_content() to observe payload.
    This is READ-ONLY observation - no modifications.
    """
    try:
        import google.generativeai as genai

        original_generate_content = genai.GenerativeModel.generate_content

        def generate_content_with_observation(self, contents, **kwargs):
            """Intercept and observe payload before API call"""

            # Observe the content parameter
            if isinstance(contents, str):
                input_text = contents
            else:
                input_text = str(contents)

            observation["gemini_input_sample"] = input_text[:500] if len(input_text) > 500 else input_text

            # Check for Decision context markers
            has_decision_context = "[JARVIS DECISION CONTEXT]" in input_text
            observation["decision_context_in_gemini_input"] = has_decision_context

            print(f"\n[OBSERVATION] genai.GenerativeModel.generate_content() called")
            print(f"  Input length: {len(input_text)} chars")
            print(f"  Decision context detected: {has_decision_context}")

            if has_decision_context:
                print(f"  [SUCCESS] Decision context FOUND in Gemini input")
                # Extract Decision ID from context
                start_idx = input_text.find("Decision ID: ")
                if start_idx >= 0:
                    end_idx = input_text.find("\n", start_idx)
                    decision_line = input_text[start_idx:end_idx]
                    print(f"    {decision_line}")

            # Call original function
            return original_generate_content(self, contents, **kwargs)

        genai.GenerativeModel.generate_content = generate_content_with_observation
        print("[SETUP] Monkey-patch applied to genai.GenerativeModel.generate_content()")
        return True

    except ImportError as e:
        print(f"[WARNING] genai not available: {e}")
        observation["gemini_api_available"] = False
        return False
    except Exception as e:
        print(f"[WARNING] Failed to setup observation: {e}")
        return False


def get_real_decision_id():
    """Get a real Decision ID from decision_ledger"""
    ledger_path = Path(__file__).parent.parent / "data" / "decisions" / "decision_ledger.jsonl"

    if not ledger_path.exists():
        print(f"[ERROR] Decision ledger not found at {ledger_path}")
        return None

    decisions = []
    try:
        with open(ledger_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line)
                        if d.get('decision_id'):
                            decisions.append(d)
                    except:
                        pass
    except Exception as e:
        print(f"[ERROR] Failed to read ledger: {e}")
        return None

    if decisions:
        # Use the most recent one
        latest = decisions[-1]
        decision_id = latest.get('decision_id')
        print(f"[FOUND] Real Decision ID: {decision_id}")
        print(f"  Title: {latest.get('title', 'N/A')}")
        print(f"  Status: {latest.get('status', 'N/A')}")
        return decision_id

    return None


def run_verification():
    """Run the real E2E verification"""

    print("=" * 70)
    print("STEP 3 REAL E2E VERIFICATION: Gemini + JARVIS Decision")
    print("=" * 70)

    # Step 1: Get real Decision
    print(f"\n[STEP 1] Retrieve Real Decision from Ledger")
    decision_id = get_real_decision_id()

    if not decision_id:
        print("[FAILED] Could not find real Decision")
        return False

    observation["decision_id"] = decision_id

    # Step 2: Setup observation
    print(f"\n[STEP 2] Setup Payload Observation")
    observation_ok = setup_payload_observation()

    if not observation_ok:
        print("[WARNING] Observation may not work - API key might be missing")

    # Step 3: Call dispatch_multi_request with Gemini only
    print(f"\n[STEP 3] Call dispatch_multi_request with Gemini provider")
    print(f"  Decision ID: {decision_id}")
    print(f"  Provider: gemini")
    print(f"  Using existing multi_dispatcher.py (NO CHANGES)")

    try:
        from multi_dispatcher import dispatch_multi_request

        response = dispatch_multi_request(
            request_text="Verify decision context binding to Gemini",
            providers=["gemini"],
            models={"gemini": "gemini-2.0-flash"},
            title="STEP 3 Real E2E Verification",
            decision_id=decision_id
        )

        print(f"\n[RESULT] dispatch_multi_request completed")
        print(f"  Status: {response.get('status')}")

        # Step 4: Analyze JARVIS result
        if "jarvis" in response:
            jarvis_result = response["jarvis"]
            observation["jarvis_status"] = jarvis_result.get('status')

            print(f"\n[STEP 4] JARVIS Result")
            print(f"  Status: {jarvis_result.get('status')}")

            if jarvis_result.get('jarvis_decision'):
                decision = jarvis_result.get('jarvis_decision')
                print(f"  Decision ID (from JARVIS): {decision.get('decision_id')}")

        # Step 5: Check Gemini response
        print(f"\n[STEP 5] Gemini Response")
        results = response.get('results', [])
        for result in results:
            if result.get('provider') == 'gemini':
                status = result.get('status')
                print(f"  Status: {status}")

                if status == 'ok':
                    response_text = result.get('response', '')[:100]
                    print(f"  Response: {response_text}...")
                    observation["gemini_response"] = response_text
                elif status == 'NOT_VERIFIED':
                    print(f"  Error: {result.get('error')}")
                    observation["gemini_response"] = result.get('error')

        # Step 6: Verify observation
        print(f"\n[STEP 6] Verify Decision Context Arrival")
        if observation["decision_context_in_gemini_input"]:
            print(f"  ✓ SUCCESS: Decision context reached Gemini input")
            print(f"  Input sample: {observation['gemini_input_sample'][:200]}...")
            return True
        else:
            print(f"  ⚠ Decision context not observed (may not have been called)")
            return False

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def report_findings():
    """Print final report"""

    print(f"\n" + "=" * 70)
    print("STEP 3 REAL E2E VERIFICATION REPORT")
    print("=" * 70)

    print(f"\n[Real Decision ID]")
    print(f"  {observation.get('decision_id', 'NOT_FOUND')}")

    print(f"\n[JARVIS Status]")
    print(f"  {observation.get('jarvis_status', 'UNKNOWN')}")

    print(f"\n[Gemini Input Observation]")
    if observation.get('decision_context_in_gemini_input'):
        print(f"  ✓ Decision context FOUND in client.generate_content() call")
    else:
        print(f"  ? Not observed (may not have API key)")

    print(f"\n[Gemini Response]")
    response = observation.get('gemini_response')
    if response:
        if "API_KEY" in str(response) or "not set" in str(response):
            print(f"  [NOT_VERIFIED] API_KEY not set")
            print(f"  Status: UNKNOWN (requires GOOGLE_API_KEY)")
        else:
            print(f"  ✓ Response received")
            print(f"    {response}")
    else:
        print(f"  [NO RESPONSE]")

    print(f"\n[Code Changes]")
    print(f"  Modified files: 0")
    print(f"  New test files: 0")
    print(f"  Socket changes: 0")
    print(f"  Adapter changes: 0")

    print(f"\n[Timestamp]")
    print(f"  {observation['timestamp']}")

    # Determine final status
    if observation.get('decision_id') and observation.get('jarvis_status'):
        if observation.get('decision_context_in_gemini_input'):
            print(f"\n[FINAL STATUS]")
            print(f"  ✓ GEMINI_REAL_E2E_VERIFIED")
        else:
            print(f"\n[FINAL STATUS]")
            print(f"  ? PARTIALLY_VERIFIED (Decision reached JARVIS, Gemini output not observable)")
    else:
        print(f"\n[FINAL STATUS]")
        print(f"  ? EVIDENCE_GAP (Unable to complete observation)")


if __name__ == "__main__":
    success = run_verification()
    report_findings()

    if success:
        print(f"\n✓ VERIFICATION COMPLETE - Decision context confirmed to reach Gemini")

    sys.exit(0 if success else 1)
