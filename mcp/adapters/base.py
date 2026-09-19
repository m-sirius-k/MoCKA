from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class BaseAdapter:
    def parse(self, request: dict) -> dict:
        raise NotImplementedError

    def extract_authority_context(self, request: dict) -> Optional[Dict[str, Any]]:
        """
        Extract Authority Context from request if present.
        Base implementation: check for 'authority_context' field.
        Subclasses may override for source-specific extraction (e.g., HTTP headers).

        Returns:
            dict with authority context fields, or None if absent
            Must include: authority_id, authority_context_id, verification_state
        """
        auth_ctx = request.get("authority_context")
        if auth_ctx:
            # Ensure minimal required fields
            if "authority_id" not in auth_ctx:
                return None
            return auth_ctx
        return None
