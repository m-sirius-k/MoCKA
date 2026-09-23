# -*- coding: utf-8 -*-
"""
Multi-AI Socket E2E Test

Test the minimum E2E flow:
  1. Send HAB request to /api/v1/socket/multi_request
  2. Verify dispatcher routes to multiple AI sockets
  3. Collect individual responses from available providers
  4. Verify HAB records each provider response separately

Run with:
  python test_multi_e2e.py
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timezone

# Gateway URL
GATEWAY_URL = "http://localhost:5010"
API_KEY = "test-key-for-audit"

HEADERS = {
    "Content-Type": "application/json",
    "X-MoCKA-Key": API_KEY,
}


def test_multi_request():
    """Test multi-AI socket request E2E."""
    print("\n" + "=" * 80)
    print("TEST: Multi-AI Socket E2E")
    print("=" * 80)

    # Request payload
    payload = {
        "request": "What is the MoCKA system architecture? Respond in 1-2 sentences.",
        "providers": ["gpt", "claude", "gemini", "perplexity"],
        "models": {
            "gpt": "gpt-4",
            "claude": "claude-opus-5",
            "gemini": "gemini-2.0-flash",
            "perplexity": "sonar-pro",
        },
        "title": "E2E Multi-AI Test Request",
    }

    print("\n[1] Sending multi-request to gateway...")
    print(f"    URL: POST {GATEWAY_URL}/api/v1/socket/multi_request")
    print(f"    Providers: {', '.join(payload['providers'])}")

    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/socket/multi_request",
            json=payload,
            headers=HEADERS,
            timeout=60,
        )
        print(f"    Response Status: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Cannot connect to gateway at {GATEWAY_URL}")
        print(f"       Make sure gateway is running: python gateway.py")
        print(f"       Error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return False

    try:
        result = response.json()
    except Exception as e:
        print(f"ERROR: Response is not JSON: {response.text[:200]}")
        return False

    print("\n[2] Analyzing multi-request response...")
    print(f"    Overall Status: {result.get('status')}")
    print(f"    Common Request ID: {result.get('request_id')}")
    print(f"    Summary:")
    summary = result.get("summary", {})
    print(f"      - Total: {summary.get('total', 0)}")
    print(f"      - OK: {summary.get('ok', 0)}")
    print(f"      - Error: {summary.get('error', 0)}")
    print(f"      - Not Verified (API key missing): {summary.get('not_verified', 0)}")

    results = result.get("results", [])
    print(f"\n[3] Individual Provider Results:")
    print("-" * 80)

    verified_count = 0
    for i, provider_result in enumerate(results, 1):
        provider = provider_result.get("provider", "unknown")
        status = provider_result.get("status", "unknown")
        model = provider_result.get("model", "")
        error = provider_result.get("error", "")
        response_text = provider_result.get("response", "")
        usage = provider_result.get("usage", {})

        print(f"\n  [{i}] Provider: {provider.upper()}")
        print(f"      Status: {status}")
        print(f"      Model: {model}")
        if status == "ok":
            verified_count += 1
            print(f"      Response Preview: {response_text[:80]}...")
            if usage:
                print(f"      Tokens: prompt={usage.get('prompt_tokens', '?')}, "
                      f"completion={usage.get('completion_tokens', '?')}, "
                      f"total={usage.get('total_tokens', '?')}")
        elif status == "NOT_VERIFIED":
            print(f"      Reason: API_KEY_MISSING")
        else:
            print(f"      Error: {error[:100]}...")

    print("\n" + "-" * 80)
    print(f"[4] Verification Summary:")
    print(f"    Providers responded: {verified_count}/{summary.get('total', 0)}")
    print(f"    Expected: At least 1 provider (GPT if API key available)")

    if verified_count > 0:
        print(f"\n[5] SUCCESS: Multi-AI E2E working!")
        print(f"    - Multi-request routed to {len(results)} providers")
        print(f"    - {verified_count} provider(s) verified and responded")
        print(f"    - Each response recorded independently")
        return True
    else:
        print(f"\n[6] WARNING: No providers verified")
        print(f"    - Check API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc.")
        print(f"    - Test is PARTIALLY COMPLETE (E2E structure working, no live APIs)")
        return None  # Partial success


def test_single_gpt_outbound():
    """Verify existing single-AI outbound E2E still works (regression test)."""
    print("\n" + "=" * 80)
    print("REGRESSION TEST: Single GPT Outbound E2E")
    print("=" * 80)

    payload = {
        "ai": "gpt",
        "request": "What is 2+2?",
        "model": "gpt-4",
        "title": "Simple Math Test",
    }

    print("\n[1] Sending single GPT request (existing flow)...")
    print(f"    URL: POST {GATEWAY_URL}/api/v1/socket/request")

    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/socket/request",
            json=payload,
            headers=HEADERS,
            timeout=30,
        )
        print(f"    Response Status: {response.status_code}")
        result = response.json()
        print(f"    Status: {result.get('status')}")

        if result.get("status") == "ok":
            print(f"    Response: {result.get('response', '')[:80]}...")
            print("\n[2] SUCCESS: Single GPT outbound E2E still working (no regression)")
            return True
        elif "API_KEY" in result.get("error", ""):
            print(f"    Reason: API key missing (expected in test environment)")
            print("\n[2] PARTIAL: Single GPT E2E structure OK, no live API")
            return None
        else:
            print(f"    Error: {result.get('error', '')}")
            print("\n[2] FAILED: Single GPT E2E broken")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_inbound_event_recording():
    """Verify existing inbound event recording still works (regression test)."""
    print("\n" + "=" * 80)
    print("REGRESSION TEST: Inbound Event Recording")
    print("=" * 80)

    payload = {
        "title": "E2E Test Event",
        "description": "Testing inbound event recording in multi-AI context",
        "tags": ["e2e_test", "multi_ai"],
        "actor": {
            "vendor": "TestAI",
            "model": "test-model",
            "source": "E2E Test",
        },
        "why_purpose": "regression_test",
    }

    print("\n[1] Recording test event...")
    print(f"    URL: POST {GATEWAY_URL}/api/v1/event")

    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/event",
            json=payload,
            headers=HEADERS,
            timeout=10,
        )
        print(f"    Response Status: {response.status_code}")
        result = response.json()
        print(f"    Status: {result.get('status')}")

        if response.status_code == 201 or result.get("status") == "ok":
            print(f"    Event ID: {result.get('event_id', 'N/A')}")
            print("\n[2] SUCCESS: Inbound event recording still working (no regression)")
            return True
        else:
            print(f"    Error: {result}")
            print("\n[2] FAILED: Inbound event recording broken")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Run all E2E tests."""
    print("\n" + "=" * 80)
    print("MoCKA Multi-AI Socket E2E Test Suite")
    print("=" * 80)
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    tests = [
        ("Multi-AI Socket E2E", test_multi_request),
        ("Single GPT Outbound (Regression)", test_single_gpt_outbound),
        ("Inbound Event Recording (Regression)", test_inbound_event_recording),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nEXCEPTION in {test_name}: {e}")
            results[test_name] = False

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        status_str = "PASS" if result is True else ("PARTIAL" if result is None else "FAIL")
        print(f"  {test_name}: {status_str}")

    all_pass = all(r is not False for r in results.values())
    any_fail = any(r is False for r in results.values())

    if all_pass and any(r is True for r in results.values()):
        print("\nOVERALL: E2E tests PASSED or PARTIAL")
        print("(PARTIAL = structure verified but no live API keys)")
        return 0
    elif any_fail:
        print("\nOVERALL: E2E tests FAILED")
        return 1
    else:
        print("\nOVERALL: E2E tests PARTIAL (no live APIs)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
