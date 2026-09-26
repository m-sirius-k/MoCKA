#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 2-3: Execute existing Orchestra Web path via HAB/JARVIS
Test input: MOCKA_ORCHESTRA_EXISTING_PATH_TEST_20260923
Using existing multi_dispatcher entry point
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from multi_dispatcher import dispatch_multi_request

def main():
    print("=" * 80)
    print("STEP 2-3: EXISTING ORCHESTRA WEB PATH EXECUTION")
    print("=" * 80)
    print()

    # Test input as per requirement
    test_input = "MOCKA_ORCHESTRA_EXISTING_PATH_TEST_20260923"

    print(f"[SETUP] Test Configuration")
    print(f"  Test Input: {test_input}")
    print(f"  Entry Point: gateway_multi_dispatcher (existing)")
    print(f"  Expected Path: HAB/JARVIS → MultiDispatcher → Orchestra → Claude.ai Web")
    print()

    # STEP 2: Use existing HAB/JARVIS entry (multi_dispatcher)
    print("[STEP 2] HAB/JARVIS Request")
    print(f"  Calling: dispatch_multi_request()")

    request_params = {
        "request_text": test_input,
        "providers": ["orchestra_web"],
        "models": {
            "orchestra_web": "default",
        },
        "title": "Orchestra Socket E2E Test",
        "decision_id": "ORCH_SOCKET_E2E_20260923"
    }

    print(f"  Request params: {json.dumps(request_params, indent=2)}")
    print()

    # STEP 3: Execute existing path
    print("[STEP 3] Execution Trace")

    # Track execution through each component
    results_by_component = {}

    try:
        print("  [1] HAB/JARVIS Request - Sending to MultiDispatcher...")
        response = dispatch_multi_request(**request_params)
        results_by_component['HAB/JARVIS Request'] = 'PASS'
        print(f"      ✓ Response received")
        print(f"      Status: {response.get('status')}")

    except Exception as e:
        results_by_component['HAB/JARVIS Request'] = f'FAIL: {str(e)[:50]}'
        print(f"      ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Analyze response structure
    print()
    print("[STEP 4] Path Component Verification")
    print("=" * 80)

    # Check MultiDispatcher component
    if response:
        results_by_component['MultiDispatcher'] = 'PASS'
        print(f"[2] MultiDispatcher: PASS")
        print(f"    Request ID: {response.get('request_id')}")
        print(f"    Status: {response.get('status')}")
    else:
        results_by_component['MultiDispatcher'] = 'FAIL'
        print(f"[2] MultiDispatcher: FAIL (no response)")
        return False

    # Check Orchestra dispatch
    results = response.get('results', [])
    if results:
        results_by_component['Orchestra Dispatch'] = 'PASS'
        print(f"[3] Orchestra Dispatch: PASS ({len(results)} results)")
    else:
        results_by_component['Orchestra Dispatch'] = 'FAIL'
        print(f"[3] Orchestra Dispatch: FAIL (no results)")

    # Check individual provider responses
    print(f"[4] Provider Responses:")
    for result in results:
        provider = result.get('provider', 'unknown')
        status = result.get('status', 'unknown')

        # Map to component
        if provider.lower() == 'gpt':
            comp_name = 'Playwright (via API)'
        elif provider.lower() == 'gemini':
            comp_name = 'Playwright (via API)'
        else:
            comp_name = f'Provider: {provider}'

        results_by_component[comp_name] = 'PASS' if status == 'ok' else f'FAIL: {status}'

        print(f"    {provider}: {status}")
        if status == 'ok':
            resp_text = result.get('response', '')[:80]
            print(f"      Response: {resp_text}...")

    # Check JARVIS response (indicates Orchestra chain completed)
    if 'jarvis' in response:
        jarvis_resp = response['jarvis']
        results_by_component['HAB/JARVIS Return'] = 'PASS'
        print(f"[5] HAB/JARVIS Return: PASS")
        print(f"    JARVIS Status: {jarvis_resp.get('status')}")
    else:
        results_by_component['HAB/JARVIS Return'] = 'FAIL'
        print(f"[5] HAB/JARVIS Return: FAIL (no JARVIS response)")

    # Print component-by-component results
    print()
    print("=" * 80)
    print("[FINAL] COMPONENT VERIFICATION")
    print("=" * 80)

    component_names = [
        'HAB/JARVIS Request',
        'MultiDispatcher',
        'Orchestra Dispatch',
        'Playwright (via API)',
        'HAB/JARVIS Return',
    ]

    for comp in component_names:
        status = results_by_component.get(comp, 'NOT TESTED')
        symbol = '✓' if status == 'PASS' else '✗'
        print(f"{symbol} {comp:30s} : {status}")

    # Final verdict
    print()
    print("=" * 80)
    all_pass = all(v == 'PASS' for v in results_by_component.values())

    if all_pass:
        verdict = "VERIFIED"
    elif any(v == 'PASS' for v in results_by_component.values()):
        verdict = "IMPLEMENTED BUT UNVERIFIED"
    else:
        verdict = "BLOCKED"

    print(f"EXISTING ORCHESTRA WEB E2E: {verdict}")
    print("=" * 80)

    return verdict == "VERIFIED"

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
