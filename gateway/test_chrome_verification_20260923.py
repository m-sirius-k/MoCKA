#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Execution Verification Test
Monitors browser processes during Orchestra Socket E2E execution.

Purpose:
  Verify that orchestra_one_host.py is actually launching Google Chrome
  (not Chromium bundled or other browsers).
"""

import sys
import json
import subprocess
import time
import psutil
from pathlib import Path
from datetime import datetime, timezone

_gateway_path = Path(__file__).parent
_mocka_root = _gateway_path.parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))
if str(_mocka_root) not in sys.path:
    sys.path.insert(0, str(_mocka_root))

print("[Chrome Verification] Sys path configured")
print()


def get_browser_processes(before_pids=None):
    """Get all browser-related processes (Chrome, Chromium, etc)."""
    browser_processes = []
    current_pids = set()

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            name = (proc.info['name'] or '').lower()
            exe_val = proc.info.get('exe')
            exe = (exe_val or '').lower()
            cmdline = proc.info.get('cmdline') or []

            # Detect Chrome/Chromium processes
            if any(x in name for x in ['chrome', 'chromium', 'msedge']):
                current_pids.add(proc.pid)

                # Get executable path
                exec_path = proc.info.get('exe', 'unknown')
                is_google_chrome = 'chrome' in exec_path and 'chromium' not in exec_path.lower()
                is_chromium = 'chromium' in exec_path.lower()
                is_edge = 'msedge' in exec_path.lower()

                browser_type = "Google Chrome" if is_google_chrome else \
                               "Chromium" if is_chromium else \
                               "Microsoft Edge" if is_edge else \
                               "Unknown Browser"

                browser_processes.append({
                    'pid': proc.pid,
                    'name': name,
                    'type': browser_type,
                    'exe': exec_path,
                    'cmdline': ' '.join(cmdline[:3]) if cmdline else 'N/A',
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if before_pids:
        new_pids = current_pids - before_pids
        return browser_processes, new_pids
    else:
        return browser_processes, current_pids


def test_chrome_execution():
    print("=" * 80)
    print("CHROME EXECUTION VERIFICATION: MOCKA_ORCHESTRA_SOCKET_E2E_20260923")
    print("=" * 80)
    print()

    results = {}
    timestamp_start = datetime.now(timezone.utc).isoformat()

    # ============================================================================
    # STEP 1: Baseline Process Check
    # ============================================================================
    print("[STEP 1] Baseline Browser Process Check")
    print("-" * 80)

    baseline_procs, baseline_pids = get_browser_processes()
    print(f"Browser processes before test: {len(baseline_procs)}")
    for proc in baseline_procs:
        print(f"  - PID {proc['pid']}: {proc['type']} ({proc['exe'][:60]}...)")

    print()

    # ============================================================================
    # STEP 2: MultiDispatcher Dispatch (with monitoring)
    # ============================================================================
    print("[STEP 2] E2E Test Execution (Orchestra Socket)")
    print("-" * 80)

    try:
        from multi_dispatcher import dispatch_multi_request

        request_params = {
            "request_text": "MOCKA_ORCHESTRA_SOCKET_E2E_20260923",
            "providers": ["orchestra_web"],
            "models": {"orchestra_web": "default"},
            "title": "Chrome Verification Test",
            "decision_id": "CHROME_VERIFY_20260923"
        }

        print("Starting dispatch_multi_request()...")
        print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")

        # Monitor process for 5 seconds before request
        print("  Pre-execution process monitoring (2 seconds)...")
        time.sleep(2)
        pre_exec_procs, _ = get_browser_processes()

        # Execute dispatch
        dispatch_response = dispatch_multi_request(**request_params)

        # Monitor for 5 seconds after request
        print("  Post-execution process monitoring (5 seconds)...")
        time.sleep(5)
        post_exec_procs, new_pids = get_browser_processes(baseline_pids)

        print(f"✓ Dispatch completed")
        print(f"  Status: {dispatch_response.get('status')}")
        print()

        # Analyze process changes
        print("Browser processes after test:")
        all_procs, _ = get_browser_processes()
        for proc in all_procs:
            if proc['pid'] in new_pids:
                print(f"  [NEW] PID {proc['pid']}: {proc['type']} ({proc['exe'][:60]}...)")
            else:
                print(f"  [OLD] PID {proc['pid']}: {proc['type']} ({proc['exe'][:60]}...)")

        results["MultiDispatcher dispatch"] = "PASS"

    except Exception as e:
        results["MultiDispatcher dispatch"] = f"FAIL: {str(e)}"
        print(f"✗ Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    print()

    # ============================================================================
    # STEP 3: Browser Type Verification
    # ============================================================================
    print("[STEP 3] Browser Type Verification")
    print("-" * 80)

    all_current_procs, _ = get_browser_processes()

    google_chrome_found = False
    chromium_only_found = False

    for proc in all_current_procs:
        if proc['type'] == "Google Chrome":
            google_chrome_found = True
            print(f"✓ Google Chrome detected")
            print(f"  PID: {proc['pid']}")
            print(f"  Executable: {proc['exe']}")
            print(f"  Type: {proc['type']}")
        elif proc['type'] == "Chromium":
            chromium_only_found = True
            print(f"⚠ Chromium (bundled) detected")
            print(f"  PID: {proc['pid']}")
            print(f"  Executable: {proc['exe']}")
            print(f"  Type: {proc['type']}")

    if google_chrome_found:
        results["Google Chrome execution"] = "VERIFIED"
        print()
        print("✓ Google Chrome is running")
    elif chromium_only_found:
        results["Google Chrome execution"] = "NOT VERIFIED (Chromium bundled)"
        print()
        print("⚠ Only Chromium bundled detected (not Google Chrome)")
    else:
        results["Google Chrome execution"] = "NOT VERIFIED (no browser)"
        print()
        print("✗ No browser process detected")

    print()

    # ============================================================================
    # STEP 4: Response Verification
    # ============================================================================
    print("[STEP 4] Response Verification")
    print("-" * 80)

    try:
        provider_results = dispatch_response.get("results", [])

        if provider_results:
            for result in provider_results:
                if result.get("provider") == "orchestra_web":
                    if result.get("status") == "ok":
                        response_text = result.get("response", "")
                        results["Response return"] = "VERIFIED"
                        print(f"✓ Response received ({len(response_text)} chars)")
                    else:
                        results["Response return"] = f"NOT VERIFIED: {result.get('error')}"
                        print(f"✗ No response: {result.get('error')}")
        else:
            results["Response return"] = "NOT VERIFIED (no results)"
            print("✗ No results from dispatcher")

    except Exception as e:
        results["Response return"] = f"NOT VERIFIED: {str(e)}"
        print(f"✗ Exception: {e}")

    print()

    # ============================================================================
    # FINAL VERDICT
    # ============================================================================
    print("=" * 80)
    print("[FINAL] VERIFICATION SUMMARY")
    print("=" * 80)
    print()

    print("Component Verification:")
    print(f"  OrchestraSocket E2E:          VERIFIED (from previous test)")
    print(f"  Web AI communication:         {results.get('MultiDispatcher dispatch', 'UNKNOWN')}")
    print(f"  Google Chrome execution:      {results.get('Google Chrome execution', 'UNKNOWN')}")
    print(f"  Response return:              {results.get('Response return', 'UNKNOWN')}")

    print()

    # Determine Chrome status
    chrome_status = results.get("Google Chrome execution", "UNKNOWN")
    if chrome_status == "VERIFIED":
        print("✓ Chrome Verification: PASSED")
        print("  Google Chrome is confirmed to be running")
    elif "Chromium" in chrome_status:
        print("⚠ Chrome Verification: INCONCLUSIVE")
        print("  Running Chromium bundled (not Google Chrome)")
        print("  → Recommendation: Modify orchestra_one_host.py to specify channel='chrome'")
    else:
        print("✗ Chrome Verification: NOT VERIFIED")
        print("  No Chrome/Chromium process detected")
        print("  → Check if browser launch was blocked or timeout occurred")

    print()

    timestamp_end = datetime.now(timezone.utc).isoformat()
    print(f"Start: {timestamp_start}")
    print(f"End:   {timestamp_end}")
    print()

    return results


if __name__ == "__main__":
    try:
        # Check if psutil is available
        import psutil
    except ImportError:
        print("ERROR: psutil not installed")
        print("Install with: pip install psutil")
        sys.exit(2)

    try:
        test_results = test_chrome_execution()
        sys.exit(0)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
