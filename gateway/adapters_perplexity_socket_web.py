# -*- coding: utf-8 -*-
"""
Perplexity Socket Web - Browser-based Perplexity Socket (Orchestra CDP pattern)

Purpose:
  Connect to Perplexity via browser using existing logged-in session (via CDP).
  Falls back to API if CDP is not available.
"""

import asyncio
import os
from socket_base import submit_to_hab


class PerplexitySocketWeb:
    """Perplexity Socket with browser support (Orchestra CDP pattern)"""

    def __init__(self):
        self.ai_name = 'Perplexity'
        self.ai_config = {
            'url': 'https://www.perplexity.ai',
            # Updated selectors for Perplexity - wider fallback patterns
            'input_selector': 'textarea, input[type="text"], [contenteditable="true"], [role="textbox"], [role="combobox"]',
            'response_selector': '.prose, div[data-message-author-role="assistant"], .answer, [role="region"], .response',
            'stop_selector': 'button[aria-label="Stop"]',
            'is_contenteditable': False,
        }

    def request(self, request_text: str, model: str = "sonar-pro",
                title: str = "Perplexity Web Request") -> dict:
        """
        Send request to Perplexity via browser (CDP) or fall back to API.

        Args:
            request_text: Text to send to Perplexity
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
                "error": f"Perplexity Socket Web error: {str(e)}",
                "model": model,
            }

    def _request_web(self, request_text: str, model: str, title: str) -> dict:
        """Query Perplexity via browser using existing session"""
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
                    "scope": ["perplexity-web"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {result['response'][:100]}",
                }
                ai_identity = f"perplexity_web_{model}"

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
                    "error": f"Perplexity web query failed: {result.get('error')}",
                    "model": model,
                    "method": result['method'],
                }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Perplexity web error: {str(e)}",
                "model": model,
            }

    def _request_api(self, request_text: str, model: str, title: str) -> dict:
        """Fall back to API if CDP not available"""
        try:
            from adapter_perplexity import call_api

            api_result = call_api(request_text, model)

            if api_result.get("status") == "ok":
                hab_context = {
                    "decision_id": None,
                    "scope": ["perplexity-api"],
                    "authority_role": "AI_RESPONSE",
                    "note": f"{title}: {api_result.get('response', '')[:100]}",
                }
                ai_identity = f"perplexity_response_{model}"

                from hab_bridge import HABBridge
                bridge = HABBridge()
                bridge_result = bridge.submit_from_ai(ai_identity, hab_context)

                api_result["hab_response_id"] = bridge_result.get("request_id")
                api_result["method"] = "api"

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Perplexity API error: {str(e)}",
                "model": model,
            }
