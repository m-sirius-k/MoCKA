#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression Test: STEP 11-D Inbound AI → Socket → HAB path
Verify existing functionality is not broken.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gateway"))

def test_claude_inbound():
    """Test Claude inbound: adapter → Socket.submit() → HAB"""
    print("\n=== CLAUDE INBOUND (Existing Path) ===")

    from adapters_claude_socket import ClaudeSocket

    socket = ClaudeSocket()
    result = socket.submit(
        model="claude-opus-5",
        runtime="Claude",
        title="Regression Test",
        description="Testing existing inbound path",
        tags=["test", "regression"]
    )

    print(f"Status: {result.get('status')}")
    print(f"Request ID: {result.get('request_id')}")
    print(f"State: {result.get('state')}")
    print(f"Decision ID: {result.get('decision_id')}")
    print(f"AI Identity: {result.get('ai_identity')}")

    expected = ["request_id", "state"]
    missing = [k for k in expected if k not in result]

    if not missing:
        print("REGRESSION TEST: PASS")
        return True
    else:
        print(f"REGRESSION TEST: FAIL - Missing {missing}")
        return False


def test_gpt_inbound():
    """Test GPT inbound: adapter → Socket.submit() → HAB"""
    print("\n=== GPT INBOUND (Existing Path) ===")

    from adapters_gpt_socket import GPTSocket

    socket = GPTSocket()
    result = socket.submit(
        model="gpt-4",
        runtime="ChatGPT",
        title="Regression Test",
        description="Testing existing inbound path",
        tags=["test", "regression"]
    )

    print(f"Status: {result.get('status')}")
    print(f"Request ID: {result.get('request_id')}")
    print(f"State: {result.get('state')}")
    print(f"Decision ID: {result.get('decision_id')}")
    print(f"AI Identity: {result.get('ai_identity')}")

    expected = ["request_id", "state"]
    missing = [k for k in expected if k not in result]

    if not missing:
        print("REGRESSION TEST: PASS")
        return True
    else:
        print(f"REGRESSION TEST: FAIL - Missing {missing}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("REGRESSION TEST: STEP 11-D Inbound Path")
    print("=" * 70)

    results = []
    results.append(("Claude Inbound", test_claude_inbound()))
    results.append(("GPT Inbound", test_gpt_inbound()))

    print("\n" + "=" * 70)
    print("REGRESSION TEST SUMMARY")
    print("=" * 70)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:30} {status}")
