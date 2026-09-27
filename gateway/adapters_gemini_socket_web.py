# -*- coding: utf-8 -*-
"""
Gemini Socket Web - Browser-based Gemini Socket (Orchestra CDP pattern)

Purpose:
  Connect to Gemini via browser using existing logged-in session (via CDP).
  Falls back to API if CDP is not available.
"""

import asyncio
import os
from socket_base import submit_to_hab


class GeminiSocketWeb:
    """Gemini Socket with browser support (Orchestra CDP pattern)"""

    def __init__(self):
        self.ai_name = 'Gemini'
        self.ai_config = {
            'url': 'https://gemini.google.com/app',
            'input_selector': '.ql-editor, textarea[aria-label*="Message"]',
            'response_selector': 'model-response .response-container, div[data-message-author-role="assistant"]',
            'stop_selector': 'button[aria-label="Stop response"]',
            'is_contenteditable': True,
        }

    def request(self, request_text: str, model: str = "gemini-2.0-flash",
                title: str = "Gemini Web Request") -> dict:
        """
        Send request to Gemini via browser (CDP) or fall back to API.

        Args:
            request_text: Text to send to Gemini
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
                "error": f"Gemini Socket Web error: {str(e)}",
                "model": model,
            }

    def _request_web(self, request_text: str, model: str, title: str) -> dict:
        """Query Gemini via browser using existing session"""
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
                    "scope": ["gemini-web"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {result['response'][:100]}",
                }
                ai_identity = f"gemini_web_{model}"

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
                    "error": f"Gemini web query failed: {result.get('error')}",
                    "model": model,
                    "method": result['method'],
                }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Gemini web error: {str(e)}",
                "model": model,
            }

    def _request_api(self, request_text: str, model: str, title: str) -> dict:
        """Fall back to API if CDP not available"""
        try:
            from adapter_gemini import call_api

            api_result = call_api(request_text, model)

            if api_result.get("status") == "ok":
                hab_context = {
                    "decision_id": None,
                    "scope": ["gemini-api"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {api_result.get('response', '')[:100]}",
                }
                ai_identity = f"gemini_response_{model}"

                from hab_bridge import HABBridge
                bridge = HABBridge()
                bridge_result = bridge.submit_from_ai(ai_identity, hab_context)

                api_result["hab_response_id"] = bridge_result.get("request_id")
                api_result["method"] = "api"

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Gemini API error: {str(e)}",
                "model": model,
            }
