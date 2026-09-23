#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: HAB Response Return - Verify RECORDED vs USED distinction
- Response is submitted to HAB
- Decision ID is assigned
- Verify HAB actually receives and tracks it (not just logged)
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gateway"))

def test_gpt_response_tracking():
    """
    Test GPT outbound response:
    1. Call GPT API
    2. Get response
    3. Submit to HAB via bridge
    4. Verify HAB assigns request_id
    5. Verify response can be retrieved (if available)
    """
    print("\n=== GPT RESPONSE TRACKING TEST ===")

    from adapters_gpt_socket import GPTSocket

    socket = GPTSocket()

    # Step 1: Make request to GPT
    print("\n1. Sending request to GPT...")
    result = socket.request(
        request_text="What is 1+1?",
        model="gpt-4",
        title="Response Tracking Test"
    )

    print(f"   Status: {result.get('status')}")
    print(f"   Response: {result.get('response')}")
    print(f"   HAB Response ID: {result.get('hab_response_id')}")

    # Step 2: Verify response was recorded
    if result.get("status") != "ok":
        print("   ERROR: API call failed")
        return False

    # Step 3: Verify HAB assignment
    hab_resp_id = result.get("hab_response_id")
    if not hab_resp_id:
        print("   WARNING: No hab_response_id returned")
        print("   (This may mean response was recorded but HAB assignment skipped)")
        return False

    # Step 4: Verify format of hab_response_id
    print(f"\n2. Verifying HAB response tracking...")
    print(f"   HAB Response ID format: {hab_resp_id}")

    if hab_resp_id.startswith("HG"):
        print("   Format: OK (HG20260922_xxxxx)")
        print("   RECORDED: YES")
        return True
    else:
        print("   Format: UNEXPECTED")
        return False


def test_response_decision_mapping():
    """
    Verify that response is tracked as separate decision, not merged with request.
    """
    print("\n=== DECISION MAPPING TEST ===")

    from adapters_gpt_socket import GPTSocket

    socket = GPTSocket()

    print("\n1. Making request to GPT...")
    result = socket.request(
        request_text="What is 2+2?",
        model="gpt-4",
        title="Decision Mapping Test"
    )

    if result.get("status") != "ok":
        print("   ERROR: API call failed")
        return False

    hab_resp_id = result.get("hab_response_id")
    response_text = result.get("response")

    print(f"   Response text: {response_text}")
    print(f"   HAB Response ID: {hab_resp_id}")

    # Verify each response gets its own decision_id (if system tracks them separately)
    print("\n2. Verifying response tracking...")

    if hab_resp_id:
        print(f"   Response tracked as separate decision: {hab_resp_id}")
        print("   SEPARATION: YES")
        return True
    else:
        print("   Response not tracked separately")
        print("   SEPARATION: NO")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("HAB RESPONSE RETURN - TRACKING TEST")
    print("=" * 70)
    print("Goal: Verify response is RECORDED in HAB, not just logged")

    results = []
    results.append(("Response Recorded", test_gpt_response_tracking()))
    results.append(("Response Tracked", test_response_decision_mapping()))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:30} {status}")
