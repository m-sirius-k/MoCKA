# -*- coding: utf-8 -*-
"""
Gemini Socket - Google Gemini AI Provider Socket
"""

from socket_base import submit_to_hab


class GeminiSocket:
    """Minimal Gemini Socket using common HAB submission."""

    def submit(self, model: str, runtime: str, title: str,
               description: str, tags: list = None) -> dict:
        """Submit Gemini request to HAB."""
        return submit_to_hab(model, runtime, title, description, tags)

    def request(self, request_text: str, model: str = "gemini-2.0-flash",
                title: str = "Gemini API Request") -> dict:
        """
        Outbound: Send request to Google Gemini API and return response.
        Calls adapter_gemini.call_api() directly.

        Args:
            request_text: Text to send to Gemini
            model: Google model identifier
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

            return api_result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Gemini Socket request error: {str(e)}",
                "model": model,
            }
