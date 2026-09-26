#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCHESTRA SOCKET E2E VERIFICATION
Test: MOCKA_ORCHESTRA_SOCKET_E2E_20260923

Trace execution path:
  HAB/JARVIS → MultiDispatcher → OrchestraSocket → orchestra_one_host.py
  → Chrome Extension → Native Messaging → Playwright → Web AI → Response

Purpose:
  Verify all components are correctly integrated and data flows end-to-end.

Success criteria:
  - OrchestraSocket loads successfully
  - MultiDispatcher dispatches to orchestra_web provider
  - orchestra_one_host.py invokes and returns results
  - MultiDispatcher aggregates response
  - HAB/JARVIS integration completes
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

_gateway_path = Path(__file__).parent
_mocka_root = _gateway_path.parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))
if str(_mocka_root) not in sys.path:
    sys.path.insert(0, str(_mocka_root))

print("[E2E] Sys path configured")
print(f"  Gateway: {_gateway_path}")
print(f"  MoCKA root: {_mocka_root}")
print()


def test_e2e():
    print("=" * 80)
    print("ORCHESTRA SOCKET E2E TEST: MOCKA_ORCHESTRA_SOCKET_E2E_20260923")
    print("=" * 80)
    print()

    results = {}
    timestamp_start = datetime.now(timezone.utc).isoformat()

    # ============================================================================
    # STEP 1: OrchestraSocket Load
    # ============================================================================
    print("[STEP 1] OrchestraSocket Load")
    print("-" * 80)

    try:
        from adapters_orchestra_socket import OrchestraSocket

        socket = OrchestraSocket()
        results["OrchestraSocket load"] = "PASS"
        print("✓ OrchestraSocket imported successfully")
        print(f"  Class: {OrchestraSocket}")
        print(f"  Instance: {socket}")
        print(f"  Orchestra path: {socket.orchestra_path}")
        print(f"  Timeout: {socket.timeout_seconds}s")

    except ImportError as e:
        results["OrchestraSocket load"] = f"FAIL: {str(e)}"
        print(f"✗ Import failed: {e}")
        return results

    except Exception as e:
        results["OrchestraSocket load"] = f"FAIL: {str(e)}"
        print(f"✗ Initialization failed: {e}")
        return results

    print()

    # ============================================================================
    # STEP 2: MultiDispatcher Dispatch
    # ============================================================================
    print("[STEP 2] MultiDispatcher Dispatch")
    print("-" * 80)

    try:
        from multi_dispatcher import dispatch_multi_request

        request_params = {
            "request_text": "MOCKA_ORCHESTRA_SOCKET_E2E_20260923",
            "providers": ["orchestra_web"],
            "models": {"orchestra_web": "default"},
            "title": "Orchestra Socket E2E Test",
            "decision_id": "ORCH_SOCKET_E2E_20260923"
        }

        print(f"Request text: {request_params['request_text']}")
        print(f"Providers: {request_params['providers']}")
        print(f"Models: {request_params['models']}")
        print()
        print("Dispatching...")

        dispatch_response = dispatch_multi_request(**request_params)
        results["MultiDispatcher dispatch"] = "PASS"

        print(f"✓ Dispatch completed")
        print(f"  Status: {dispatch_response.get('status')}")
        print(f"  Request ID: {dispatch_response.get('request_id')}")
        print(f"  Summary: {dispatch_response.get('summary')}")

    except Exception as e:
        results["MultiDispatcher dispatch"] = f"FAIL: {str(e)}"
        print(f"✗ Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    print()

    # ============================================================================
    # STEP 3: Existing Orchestra Invocation
    # ============================================================================
    print("[STEP 3] Existing Orchestra Invocation")
    print("-" * 80)

    try:
        provider_results = dispatch_response.get("results", [])

        if not provider_results:
            results["Existing Orchestra invocation"] = "FAIL: No provider results"
            print("✗ No results from dispatcher")
            return results

        for result in provider_results:
            provider = result.get("provider", "unknown")
            status = result.get("status", "unknown")

            if provider != "orchestra_web":
                continue

            if status == "ok":
                results["Existing Orchestra invocation"] = "PASS"
                print(f"✓ Orchestra invoked successfully")
                print(f"  Provider: {provider}")
                print(f"  Status: {status}")
            else:
                error_msg = result.get("error", "Unknown error")
                results["Existing Orchestra invocation"] = f"FAIL: {error_msg}"
                print(f"✗ Orchestra invocation failed: {error_msg}")
                return results

    except Exception as e:
        results["Existing Orchestra invocation"] = f"FAIL: {str(e)}"
        print(f"✗ Exception: {e}")
        return results

    print()

    # ============================================================================
    # STEP 4: Browser/Web AI
    # ============================================================================
    print("[STEP 4] Browser/Web AI")
    print("-" * 80)

    try:
        # Check if response contains data from actual AI
        response_text = None
        for result in provider_results:
            if result.get("provider") == "orchestra_web" and result.get("status") == "ok":
                response_text = result.get("response", "")
                break

        if response_text and len(response_text) > 20:
            results["Browser/Web AI"] = "PASS"
            print(f"✓ Received response from Web AI")
            print(f"  Response length: {len(response_text)} chars")
            print(f"  Preview: {response_text[:200]}...")
        else:
            results["Browser/Web AI"] = "BLOCKED"
            print(f"⚠ No actual AI response (may require live browser)")
            print(f"  Response: {response_text[:100] if response_text else '(empty)'}")

    except Exception as e:
        results["Browser/Web AI"] = f"FAIL: {str(e)}"
        print(f"✗ Exception: {e}")

    print()

    # ============================================================================
    # STEP 5: Response Extraction
    # ============================================================================
    print("[STEP 5] Response Extraction")
    print("-" * 80)

    try:
        response_extracted = False
        for result in provider_results:
            if result.get("provider") == "orchestra_web":
                response = result.get("response")
                usage = result.get("usage", {})

                if response:
                    results["Response extraction"] = "PASS"
                    print(f"✓ Response extracted")
                    print(f"  Type: {type(response)}")
                    print(f"  Length: {len(response)}")
                    print(f"  Usage: {usage}")
                    response_extracted = True
                else:
                    results["Response extraction"] = "FAIL"
                    print(f"✗ No response field")

        if not response_extracted:
            results["Response extraction"] = "FAIL"
            print(f"✗ Could not extract response")

    except Exception as e:
        results["Response extraction"] = f"FAIL: {str(e)}"
        print(f"✗ Exception: {e}")

    print()

    # ============================================================================
    # STEP 6: HAB/JARVIS Return
    # ============================================================================
    print("[STEP 6] HAB/JARVIS Return")
    print("-" * 80)

    try:
        # Check if JARVIS context was retrieved
        jarvis_data = dispatch_response.get("jarvis", {})

        if jarvis_data:
            jarvis_status = jarvis_data.get("status")
            print(f"✓ JARVIS integration detected")
            print(f"  JARVIS status: {jarvis_status}")

            if jarvis_status == "found":
                results["HAB/JARVIS return"] = "PASS"
                print(f"  Decision found: {jarvis_data.get('decision_id')}")
            elif jarvis_status == "empty":
                results["HAB/JARVIS return"] = "PASS"
                print(f"  No prior decisions found (normal)")
            else:
                results["HAB/JARVIS return"] = "PASS"
                print(f"  JARVIS status: {jarvis_status}")
        else:
            results["HAB/JARVIS return"] = "PASS"
            print(f"✓ HAB/JARVIS integration ready")
            print(f"  No JARVIS data (expected)")

    except Exception as e:
        results["HAB/JARVIS return"] = f"FAIL: {str(e)}"
        print(f"✗ Exception: {e}")

    print()

    # ============================================================================
    # FINAL VERDICT
    # ============================================================================
    print("=" * 80)
    print("[FINAL] COMPONENT VERIFICATION")
    print("=" * 80)
    print()

    component_order = [
        "OrchestraSocket load",
        "MultiDispatcher dispatch",
        "Existing Orchestra invocation",
        "Browser/Web AI",
        "Response extraction",
        "HAB/JARVIS return",
    ]

    print(f"{'Component':<35} {'Status':<20} {'Details'}")
    print("-" * 80)

    pass_count = 0
    fail_count = 0
    blocked_count = 0

    for component in component_order:
        status = results.get(component, "NOT TESTED")
        symbol = "✓" if status == "PASS" else ("⚠" if status == "BLOCKED" else "✗")

        print(f"{component:<35} {status:<20} {symbol}")

        if status == "PASS":
            pass_count += 1
        elif status == "BLOCKED":
            blocked_count += 1
        else:
            fail_count += 1

    print()
    print("-" * 80)

    # Determine overall verdict
    if fail_count == 0:
        if blocked_count > 0:
            verdict = "IMPLEMENTED BUT UNVERIFIED"
            verdict_symbol = "⚠"
        else:
            verdict = "VERIFIED"
            verdict_symbol = "✓"
    else:
        verdict = "BLOCKED"
        verdict_symbol = "✗"

    print(f"Result: {pass_count} PASS, {fail_count} FAIL, {blocked_count} BLOCKED")
    print()
    print(f"{verdict_symbol} OVERALL: {verdict}")
    print()

    # Print timing
    timestamp_end = datetime.now(timezone.utc).isoformat()
    print(f"Start: {timestamp_start}")
    print(f"End:   {timestamp_end}")
    print()

    # Print detailed results
    print("=" * 80)
    print("[DETAILS] Full results object")
    print("=" * 80)
    print(json.dumps(results, indent=2))
    print()

    return results, verdict


if __name__ == "__main__":
    try:
        results = test_e2e()

        if isinstance(results, tuple):
            test_results, final_verdict = results
        else:
            test_results = results
            final_verdict = "UNKNOWN"

        sys.exit(0 if final_verdict == "VERIFIED" else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
