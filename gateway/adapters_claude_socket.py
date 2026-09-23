# -*- coding: utf-8 -*-
"""
Claude Socket - Minimal adapter layer between Claude tool and HAB Bridge.

Purpose:
  Normalize Claude-specific context to HAB-compatible format.
  Single entry point for Claude AI Socket integration.

Date: 2026-09-22
Status: Minimal implementation (Socket boundary only)
"""

import sys
from pathlib import Path

# Add gateway directory to path for hab_bridge import
_gateway_path = Path(__file__).parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))

from hab_bridge import HABBridge


class ClaudeSocket:
    """
    Minimal Claude AI Socket.

    Responsibility:
      - Receive Claude-specific context (title, description, tags, model, runtime)
      - Normalize to HAB-compatible payload
      - Call HABBridge
      - Return HAB result unmodified

    Does NOT:
      - Create new abstractions
      - Add validation beyond HABBridge
      - Change request_id, ai_identity, or decision_id semantics
      - Implement provider framework
    """

    def __init__(self):
        """Initialize Claude Socket with HABBridge."""
        self.bridge = HABBridge()

    def submit(self, model: str, runtime: str, title: str,
               description: str, tags: list = None) -> dict:
        """
        Submit Claude request to HAB via Bridge.

        Args:
            model: Claude model identifier (e.g., "claude-opus-5")
            runtime: Runtime context (e.g., "Claude")
            title: Event title
            description: Event description / context
            tags: Optional tags list

        Returns:
            {
                "status": "ok" | "error",
                "request_id": str (if ok),
                "state": "PENDING" (if ok),
                "decision_id": str (if ok),
                "ai_identity": str (if ok),
                "error": str (if error)
            }

        Notes:
            - ai_identity is set to f"{model}_{runtime}"
            - Does NOT change HAB payload semantics
            - Does NOT modify decision_id generation
            - Bridge handles all HAB-specific logic
        """
        try:
            # Build HAB context (same structure as before)
            hab_context = {
                "decision_id": None,  # Let bridge generate
                "scope": tags or ["default"],
                "authority_role": "AI_AUTHORITY",
                "note": description or title,
            }

            # Call HAB Bridge with Claude identity
            ai_identity = f"{model}_{runtime}"
            bridge_result = self.bridge.submit_from_ai(ai_identity, hab_context)

            return bridge_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Claude Socket error: {str(e)}",
                "ai_identity": f"{model}_{runtime}",
            }

    def request(self, request_text: str, model: str = "claude-opus-5",
                title: str = "Claude API Request") -> dict:
        """
        Outbound: Send request to Claude API and return response.
        Calls adapter_claude.call_api() directly.

        Args:
            request_text: Text to send to Claude
            model: Claude model identifier
            title: Title for HAB response logging

        Returns:
            {
                "status": "ok" | "error",
                "response": str (if ok),
                "model": str,
                "usage": dict (if ok),
                "hab_response_id": str (from HAB notification),
                "error": str (if error),
            }
        """
        try:
            from adapter_claude import call_api

            api_result = call_api(request_text, model)

            if api_result.get("status") == "ok":
                hab_context = {
                    "decision_id": None,
                    "scope": ["claude-api"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {api_result.get('response', '')[:100]}",
                }
                ai_identity = f"claude_response_{model}"
                bridge_result = self.bridge.submit_from_ai(ai_identity, hab_context)

                api_result["hab_response_id"] = bridge_result.get("request_id")

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Claude Socket request error: {str(e)}",
                "model": model,
            }
