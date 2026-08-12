# -*- coding: utf-8 -*-
"""
Actor_ID Binding Module
Phase 2: MoCKA Boundary Enforcement - Actor Identity Verification
Ref: DC_20260812_002, DC_20260812_003

This module establishes the canonical binding between:
  X-MoCKA-Key (authentication token) -> authenticated_identity -> actor_id

Core principle: Authenticated identity is the canonical source.
Payload actor_id must be verified against this canonical source.
On mismatch -> fail-closed (reject with 401/403).
"""
import os
from typing import Optional

# X-MoCKA-Key to Actor_ID Mapping
# Canonical source for authenticated identity
# Format: API_KEY -> actor_id
_KEY_TO_ACTOR_MAPPING = {
    # Core MoCKA actors
    "mocka_system": "mocka_system",
    "mocka_gateway": "mocka_gateway",
    "claude_executor": "claude",
    "gpt_executor": "gpt",
    "gemini_executor": "gemini",
    "copilot_executor": "copilot",
    "perplexity_executor": "perplexity",
    "genspark_executor": "genspark",
}

# Load environment-configured mappings (can override defaults)
_ENV_KEYS = os.environ.get("MOCKA_API_KEYS", "").split(",")
if _ENV_KEYS and _ENV_KEYS[0]:
    # First API key defaults to 'system' if not explicitly mapped
    _KEY_TO_ACTOR_MAPPING[_ENV_KEYS[0].strip()] = os.environ.get("MOCKA_SYSTEM_ACTOR", "mocka_system")


def get_authenticated_actor_id(api_key: str) -> Optional[str]:
    """
    Derive authenticated actor_id from X-MoCKA-Key.

    This is the CANONICAL SOURCE for actor identity.
    Returns the actor_id associated with this API key, or None if not found.

    Args:
        api_key: The X-MoCKA-Key header value

    Returns:
        actor_id if key is valid, None otherwise
    """
    if not api_key:
        return None
    api_key = api_key.strip()
    return _KEY_TO_ACTOR_MAPPING.get(api_key)


def verify_actor_id_binding(api_key: str, payload_actor_id: Optional[str]) -> bool:
    """
    Verify that payload actor_id matches authenticated identity.

    Phase 2 Boundary Enforcement Rule:
    - If payload contains actor_id, it MUST match the authenticated identity
    - If payload lacks actor_id and it's required, FAIL
    - If authenticated identity cannot be determined, FAIL

    Args:
        api_key: The X-MoCKA-Key header value
        payload_actor_id: The actor_id from request payload (may be None/empty)

    Returns:
        True if verification passes (fail-closed on any failure)
        False if verification fails
    """
    # Derive canonical authenticated identity
    authenticated_actor = get_authenticated_actor_id(api_key)
    if authenticated_actor is None:
        # Unknown API key -> fail-closed
        return False

    # If payload has actor_id, it must match authenticated identity
    if payload_actor_id:
        payload_actor_id = str(payload_actor_id).strip()
        if payload_actor_id != authenticated_actor:
            # Identity mismatch -> fail-closed
            return False
    # else: payload lacks actor_id, but doesn't fail yet
    # (some endpoints may allow omission; the calling code decides)

    return True


def get_request_actor_id(api_key: str, payload_actor_id: Optional[str]) -> Optional[str]:
    """
    Get the authoritative actor_id for an event after verification.

    This should ONLY be called after verify_actor_id_binding() returns True.
    Returns the authenticated actor_id (never the payload version).

    Args:
        api_key: The X-MoCKA-Key header value
        payload_actor_id: The actor_id from request payload (for audit, not used for derivation)

    Returns:
        The canonical actor_id, derived from authenticated identity only
    """
    authenticated_actor = get_authenticated_actor_id(api_key)
    return authenticated_actor
