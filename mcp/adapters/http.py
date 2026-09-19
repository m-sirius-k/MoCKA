from .base import BaseAdapter
from typing import Optional, Dict, Any


class HTTPAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "endpoint": request.get("endpoint"),
            "method": request.get("method"),
            "body": request.get("body"),
        }

    def extract_authority_context(self, request: dict) -> Optional[Dict[str, Any]]:
        """
        Extract Authority Context from HTTP request.
        Sources (in order):
        1. Explicit 'authority_context' field in request payload (for testing)
        2. 'Authorization' header (for production — format TBD)
        3. None if absent
        """
        # Explicit authority_context in payload (sandbox/testing)
        auth_ctx = request.get("authority_context")
        if auth_ctx and "authority_id" in auth_ctx:
            return auth_ctx

        # TODO: Extract from Authorization header (future)
        # auth_header = request.get("headers", {}).get("Authorization")
        # if auth_header: parse and return authority context

        return None
