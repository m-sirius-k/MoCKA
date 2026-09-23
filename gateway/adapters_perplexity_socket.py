# -*- coding: utf-8 -*-
"""
Perplexity Socket - Perplexity AI Provider Socket
"""

from socket_base import submit_to_hab


class PerplexitySocket:
    """Minimal Perplexity Socket using common HAB submission."""

    def submit(self, model: str, runtime: str, title: str,
               description: str, tags: list = None) -> dict:
        """Submit Perplexity request to HAB."""
        return submit_to_hab(model, runtime, title, description, tags)

    def request(self, request_text: str, model: str = "sonar-pro",
                title: str = "Perplexity API Request") -> dict:
        """
        Outbound: Send request to Perplexity API and return response.
        Calls adapter_perplexity.call_api() directly.

        Args:
            request_text: Text to send to Perplexity
            model: Perplexity model identifier
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

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Perplexity Socket request error: {str(e)}",
                "model": model,
            }
