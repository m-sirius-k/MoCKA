# -*- coding: utf-8 -*-
"""
socket_base.py - Minimal common Socket implementation for all AI providers.

Purpose:
  Extract duplicate HABBridge integration code.
  Provide a simple function, not a class hierarchy.
  Each provider socket imports and calls this function.

Design:
  - NO class inheritance
  - NO factory or registry
  - Simple function: submit_to_hab()
  - Reused by all provider sockets (Claude, GPT, Gemini, Perplexity, Copilot, GenSpark)

Date: 2026-09-22
Status: Common Socket utility function
"""

import sys
from pathlib import Path

# Add gateway directory to path
_gateway_path = Path(__file__).parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))

from hab_bridge import HABBridge


def submit_to_hab(model: str, runtime: str, title: str,
                  description: str, tags: list = None) -> dict:
    """
    Submit AI request to HAB via Bridge.

    Common function used by all provider sockets.
    Eliminates duplicate HABBridge integration code.

    Args:
        model: AI model identifier (e.g., "claude-opus-5", "gpt-4")
        runtime: Runtime context (e.g., "Claude", "GPT")
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
        - scope defaults to tags or ["default"]
        - authority_role is fixed as "AI_AUTHORITY"
        - note is description or title
    """
    try:
        bridge = HABBridge()

        # Build HAB context (same structure for all providers)
        hab_context = {
            "decision_id": None,  # Let bridge generate
            "scope": tags or ["default"],
            "authority_role": "AI_AUTHORITY",
            "note": description or title,
        }

        # Call HAB Bridge with AI identity
        ai_identity = f"{model}_{runtime}"
        bridge_result = bridge.submit_from_ai(ai_identity, hab_context)

        return bridge_result

    except Exception as e:
        return {
            "status": "error",
            "error": f"Socket error: {str(e)}",
            "ai_identity": f"{model}_{runtime}",
        }
