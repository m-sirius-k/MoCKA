#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Socket Test: HAB → Socket → AI API → Response → HAB
Test Claude and GPT outbound calls.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gateway"))

def test_adapter_functions():
    """Test adapter API call functions."""
    print("\n=== ADAPTER LAYER TEST ===")

    # Claude adapter
    print("\n1. Adapter Claude - call_api()")
    from adapter_claude import call_api as claude_call
    claude_result = claude_call("What is 2+2?", "claude-opus-5")
    print(f"   Status: {claude_result.get('status')}")
    print(f"   Error: {claude_result.get('error')}")

    # GPT adapter
    print("\n2. Adapter GPT - call_api()")
    from adapter_gpt import call_api as gpt_call
    gpt_result = gpt_call("What is 2+2?", "gpt-4")
    print(f"   Status: {gpt_result.get('status')}")
    if gpt_result.get('status') == 'ok':
        print(f"   Response: {gpt_result.get('response', '')[:80]}...")
        print(f"   Usage: {gpt_result.get('usage')}")
    else:
        print(f"   Error: {gpt_result.get('error')}")


def test_socket_functions():
    """Test Socket layer request() functions."""
    print("\n=== SOCKET LAYER TEST ===")

    # Claude Socket
    print("\n3. Claude Socket - request()")
    from adapters_claude_socket import ClaudeSocket
    claude_socket = ClaudeSocket()
    claude_sock_result = claude_socket.request("What is 2+2?", "claude-opus-5", "Test Claude")
    print(f"   Status: {claude_sock_result.get('status')}")
    print(f"   HAB Response ID: {claude_sock_result.get('hab_response_id')}")
    print(f"   Error: {claude_sock_result.get('error')}")

    # GPT Socket
    print("\n4. GPT Socket - request()")
    from adapters_gpt_socket import GPTSocket
    gpt_socket = GPTSocket()
    gpt_sock_result = gpt_socket.request("What is 2+2?", "gpt-4", "Test GPT")
    print(f"   Status: {gpt_sock_result.get('status')}")
    if gpt_sock_result.get('status') == 'ok':
        print(f"   Response: {gpt_sock_result.get('response', '')[:80]}...")
        print(f"   HAB Response ID: {gpt_sock_result.get('hab_response_id')}")
    else:
        print(f"   Error: {gpt_sock_result.get('error')}")


def test_gateway_endpoint_simulation():
    """Simulate gateway endpoint without HTTP (direct function call)."""
    print("\n=== GATEWAY ENDPOINT SIMULATION ===")

    # Simulate /api/v1/socket/request for GPT
    print("\n5. Simulate POST /api/v1/socket/request (GPT)")

    request_data = {
        "ai": "gpt",
        "request": "What is the capital of France?",
        "model": "gpt-4",
        "title": "Geography Test"
    }

    try:
        from adapters_gpt_socket import GPTSocket
        socket = GPTSocket()
        result = socket.request(
            request_data["request"],
            request_data["model"],
            request_data["title"]
        )

        print(f"   Status: {result.get('status')}")
        if result.get('status') == 'ok':
            print(f"   Response: {result.get('response', '')[:100]}...")
            print(f"   Model: {result.get('model')}")
            print(f"   Usage: {result.get('usage')}")
            print(f"   HAB Response ID: {result.get('hab_response_id')}")
        else:
            print(f"   Error: {result.get('error')}")

    except Exception as e:
        print(f"   Exception: {str(e)}")


if __name__ == "__main__":
    print("=" * 70)
    print("E2E SOCKET TEST: HAB → Socket → AI → Response → HAB")
    print("=" * 70)

    test_adapter_functions()
    test_socket_functions()
    test_gateway_endpoint_simulation()

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
