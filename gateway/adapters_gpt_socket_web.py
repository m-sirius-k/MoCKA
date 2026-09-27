# -*- coding: utf-8 -*-
"""
GPT Socket Web - Browser-based ChatGPT Socket (Orchestra CDP pattern)

Purpose:
  Connect to ChatGPT via browser using existing logged-in session (via CDP).
  Falls back to API if CDP is not available.

Design:
  - Uses browser_session_handler.py (shared Orchestra logic)
  - Checks CHROME_CDP_ENDPOINT first
  - Falls back to API (adapter_gpt.call_api)
  - HAB submission same as before
"""

import asyncio
import os
from socket_base import submit_to_hab


class GPTSocketWeb:
    """GPT Socket with browser support (Orchestra CDP pattern)"""

    def __init__(self):
        self.ai_name = 'ChatGPT'
        self.ai_config = {
            'url': 'https://chatgpt.com',
            'input_selector': '#prompt-textarea, div[contenteditable="true"][data-id]',
            'response_selector': '[data-message-author-role="assistant"] .markdown',
            'stop_selector': 'button[aria-label="Stop streaming"]',
            'is_contenteditable': True,
        }

    def request(self, request_text: str, model: str = "gpt-4",
                title: str = "GPT Web Request") -> dict:
        """
        Send request to ChatGPT via browser (CDP) or fall back to API.

        Args:
            request_text: Text to send to ChatGPT
            model: Model identifier
            title: Title for HAB logging

        Returns:
            {
                "status": "ok" | "error",
                "response": str (if ok),
                "model": str,
                "method": "web" | "api",
                "usage": dict (if ok),
                "error": str (if error),
            }
        """
        try:
            # Check if CDP endpoint is available
            cdp_endpoint = os.getenv('CHROME_CDP_ENDPOINT')

            if cdp_endpoint:
                # Try web browser method first
                return self._request_web(request_text, model, title)
            else:
                # Fall back to API
                return self._request_api(request_text, model, title)

        except Exception as e:
            return {
                "status": "error",
                "error": f"GPT Socket Web error: {str(e)}",
                "model": model,
            }

    def _request_web(self, request_text: str, model: str, title: str) -> dict:
        """Query ChatGPT via browser using existing session"""
        try:
            from browser_session_handler import query_ai_web_ui

            # Run async function in sync context
            result = asyncio.run(
                query_ai_web_ui(self.ai_name, self.ai_config, request_text)
            )

            if result['status'] == 'ok':
                # Submit to HAB
                hab_context = {
                    "decision_id": None,
                    "scope": ["gpt-web"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {result['response'][:100]}",
                }
                ai_identity = f"gpt_web_{model}"

                from hab_bridge import HABBridge
                bridge = HABBridge()
                bridge_result = bridge.submit_from_ai(ai_identity, hab_context)

                return {
                    "status": "ok",
                    "response": result['response'],
                    "model": model,
                    "method": result['method'],
                    "usage": {"method": "web"},
                    "hab_response_id": bridge_result.get("request_id"),
                }
            else:
                return {
                    "status": "error",
                    "error": f"ChatGPT web query failed: {result.get('error')}",
                    "model": model,
                    "method": result['method'],
                }

        except Exception as e:
            return {
                "status": "error",
                "error": f"GPT web error: {str(e)}",
                "model": model,
            }

    def _request_api(self, request_text: str, model: str, title: str) -> dict:
        """Fall back to API if CDP not available"""
        try:
            from adapter_gpt import call_api

            api_result = call_api(request_text, model)

            if api_result.get("status") == "ok":
                hab_context = {
                    "decision_id": None,
                    "scope": ["gpt-api"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {api_result.get('response', '')[:100]}",
                }
                ai_identity = f"gpt_response_{model}"

                from hab_bridge import HABBridge
                bridge = HABBridge()
                bridge_result = bridge.submit_from_ai(ai_identity, hab_context)

                api_result["hab_response_id"] = bridge_result.get("request_id")
                api_result["method"] = "api"

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"GPT API error: {str(e)}",
                "model": model,
            }
