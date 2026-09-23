#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-AI E2E Test: Claude, GPT, Gemini, Perplexity
Verify each AI's outbound path: API call → response → HAB
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gateway"))

def test_ai_outbound(ai_name, socket_class, adapter_module, model, api_key_var):
    """Generic test for any AI outbound path."""
    print(f"\n=== {ai_name.upper()} OUTBOUND TEST ===")

    api_key = os.environ.get(api_key_var)

    if not api_key:
        print(f"Status: SKIP")
        print(f"Reason: {api_key_var} not set")
        return {
            "ai": ai_name,
            "status": "NOT VERIFIED",
            "reason": f"{api_key_var} not set",
        }

    try:
        # Import socket and call request()
        socket_module = __import__(socket_class.split('.')[0])
        socket_class_obj = getattr(socket_module, socket_class.split('.')[-1])
        socket = socket_class_obj()

        # Test 1: Simple API call
        test_text = f"What is 2+2?"
        result = socket.request(test_text, model, f"Test {ai_name}")

        print(f"Test 1: '{test_text}'")
        print(f"  Status: {result.get('status')}")

        if result.get('status') != 'ok':
            print(f"  Error: {result.get('error')}")
            return {
                "ai": ai_name,
                "status": "FAILED",
                "error": result.get('error'),
            }

        print(f"  Response: {result.get('response', '')[:60]}...")
        print(f"  HAB ID: {result.get('hab_response_id', 'N/A')}")

        # Test 2: Real query
        test_text2 = f"What is Python?"
        result2 = socket.request(test_text2, model, f"Test {ai_name} 2")

        print(f"\nTest 2: '{test_text2}'")
        print(f"  Status: {result2.get('status')}")

        if result2.get('status') != 'ok':
            print(f"  Error: {result2.get('error')}")
            return {
                "ai": ai_name,
                "status": "FAILED",
                "error": result2.get('error'),
            }

        print(f"  Response: {result2.get('response', '')[:60]}...")
        print(f"  HAB ID: {result2.get('hab_response_id', 'N/A')}")

        return {
            "ai": ai_name,
            "status": "VERIFIED",
            "tests": 2,
            "hab_ids": [result.get('hab_response_id'), result2.get('hab_response_id')],
        }

    except Exception as e:
        print(f"Status: ERROR")
        print(f"Error: {str(e)}")
        return {
            "ai": ai_name,
            "status": "ERROR",
            "error": str(e),
        }


if __name__ == "__main__":
    print("=" * 70)
    print("MULTI-AI E2E TEST")
    print("=" * 70)

    results = []

    # Claude
    results.append(test_ai_outbound(
        "Claude",
        "adapters_claude_socket.ClaudeSocket",
        "adapter_claude",
        "claude-opus-5",
        "ANTHROPIC_API_KEY"
    ))

    # GPT (should work)
    results.append(test_ai_outbound(
        "GPT",
        "adapters_gpt_socket.GPTSocket",
        "adapter_gpt",
        "gpt-4",
        "OPENAI_API_KEY"
    ))

    # Gemini
    results.append(test_ai_outbound(
        "Gemini",
        "adapters_gemini_socket.GeminiSocket",
        "adapter_gemini",
        "gemini-2.0-flash",
        "GOOGLE_API_KEY"
    ))

    # Perplexity
    results.append(test_ai_outbound(
        "Perplexity",
        "adapters_perplexity_socket.PerplexitySocket",
        "adapter_perplexity",
        "sonar-pro",
        "PERPLEXITY_API_KEY"
    ))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for result in results:
        ai = result["ai"]
        status = result["status"]
        detail = ""

        if status == "VERIFIED":
            detail = f"({result['tests']} tests passed)"
        elif status == "NOT VERIFIED":
            detail = f"({result['reason']})"
        elif status in ["FAILED", "ERROR"]:
            detail = f"({result.get('error', 'unknown')})"

        print(f"{ai:15} {status:15} {detail}")

    print("\n" + "=" * 70)
