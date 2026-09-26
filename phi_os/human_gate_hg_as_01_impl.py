# phi_os/human_gate_hg_as_01_impl.py
# HG-AS-01 Implementation: Human Gate Payload Schema Validation
# Date: 2026-09-22
# Status: IMPLEMENTATION SPEC (not yet applied to phi_os/human_gate.py)
#
# Purpose: Validate payloads for HG-AS-01 Authorization State issuance
# Requirement: actor, scope, authority_role are MANDATORY for approve() actions
#
# DESIGN NOTES:
# - This module defines validation rules for payload schema
# - To be integrated into _record_transition() of phi_os/human_gate.py
# - No changes to existing state machine logic
# - Backward compatible: missing fields do not block state transitions
#   (only Authorization State issuance validation fails)

import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

# HG-AS-01 Payload Schema for approve() action
HG_AS_01_APPROVE_PAYLOAD_SCHEMA = {
    "actor": {
        "type": "string",
        "required": True,
        "description": "Human or role identifier (e.g., 'kimura_phd')",
    },
    "scope": {
        "type": "array",
        "items": {"type": "string"},
        "required": True,
        "description": "Scope of approval (e.g., ['component_A', 'component_J'])",
    },
    "authority_role": {
        "type": "string",
        "required": True,
        "description": "Role performing approval (e.g., 'HG_AUTHORITY_HOLDER_01')",
    },
    "decision_id": {
        "type": "string",
        "required": False,
        "description": "Reference to decision_record_id (optional)",
    },
    "expires_at": {
        "type": "string",
        "required": False,
        "description": "ISO8601 timestamp; null means no expiration (optional)",
    },
    "evidence_ref": {
        "type": "array",
        "items": {"type": "string"},
        "required": False,
        "description": "Evidence references (e.g., ['PAPER5_PHASE2_20260918'])",
    },
    "note": {
        "type": "string",
        "required": False,
        "description": "Approval rationale (optional)",
    },
}


def validate_payload_for_approve(payload: Dict[str, Any], request_id: str = None, conn=None) -> Tuple[bool, Optional[str]]:
    """
    Validate payload for approve() action per HG-AS-01 schema.

    Returns:
        (is_valid, error_message)
        - (True, None) if payload is valid
        - (False, error_message) if payload is invalid

    Notes:
        - actor, scope, authority_role are MANDATORY
        - authority_role must be exactly HUMAN_AUTHORITY
        - scope must match the scope in the original submit() call (if available)
        - target must match the target in the original submit() call (if available)
        - Other fields are optional
        - Empty strings are treated as missing
        - Payload validation failure DOES NOT block state transition
          (only Authorization State issuance will fail)
    """
    if not payload:
        return False, "payload is empty"

    # Check mandatory fields
    mandatory_fields = {"actor", "scope", "authority_role"}
    for field in mandatory_fields:
        if field not in payload:
            return False, f"missing mandatory field: {field}"

        value = payload[field]
        if value is None:
            return False, f"field '{field}' is None"

        if isinstance(value, str) and not value.strip():
            return False, f"field '{field}' is empty string"

        if field == "scope" and (not isinstance(value, list) or not value):
            return False, f"field 'scope' must be non-empty array"

    # Validate types
    if not isinstance(payload.get("actor"), str):
        return False, "field 'actor' must be string"

    if not isinstance(payload.get("scope"), list):
        return False, "field 'scope' must be array"

    if not isinstance(payload.get("authority_role"), str):
        return False, "field 'authority_role' must be string"

    # CRITICAL: authority_role must be HUMAN_AUTHORITY (internal Python boundary)
    # Blocks: AI_AUTHORITY, MCP_EXECUTOR, AI_AUTHORITY_OVERRIDE, etc.
    authority_role = payload.get("authority_role")
    if authority_role != "HUMAN_AUTHORITY":
        return False, f"authorization_state requires HUMAN_AUTHORITY; got {authority_role}"

    # Validate optional fields
    if "decision_id" in payload and payload["decision_id"] is not None:
        if not isinstance(payload["decision_id"], str):
            return False, "field 'decision_id' must be string or null"

    if "expires_at" in payload and payload["expires_at"] is not None:
        if not isinstance(payload["expires_at"], str):
            return False, "field 'expires_at' must be ISO8601 string or null"
        # Basic ISO8601 validation
        try:
            datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00"))
        except ValueError:
            return False, f"field 'expires_at' is not valid ISO8601: {payload['expires_at']}"

    if "evidence_ref" in payload and payload["evidence_ref"] is not None:
        if not isinstance(payload["evidence_ref"], list):
            return False, "field 'evidence_ref' must be array or null"
        if not all(isinstance(item, str) for item in payload["evidence_ref"]):
            return False, "field 'evidence_ref' items must all be strings"

    if "note" in payload and payload["note"] is not None:
        if not isinstance(payload["note"], str):
            return False, "field 'note' must be string or null"

    # If request_id and conn provided, validate scope/target consistency
    if request_id and conn:
        try:
            # Get submit event for this request_id
            submit_row = conn.execute(
                '''SELECT payload FROM human_gate_events
                   WHERE request_id = ? AND action = 'submit'
                   LIMIT 1''',
                (request_id,)
            ).fetchone()

            if submit_row:
                try:
                    submit_payload = json.loads(submit_row[0]) if submit_row[0] else {}
                except (json.JSONDecodeError, TypeError):
                    submit_payload = {}

                # Scope consistency check
                if "scope" in submit_payload and "scope" in payload:
                    submit_scope = submit_payload.get("scope", [])
                    approve_scope = payload.get("scope", [])
                    # Normalize to sorted lists for comparison
                    submit_scope_sorted = sorted(submit_scope) if isinstance(submit_scope, list) else []
                    approve_scope_sorted = sorted(approve_scope) if isinstance(approve_scope, list) else []

                    if submit_scope_sorted != approve_scope_sorted:
                        return False, f"scope mismatch: submit={submit_scope}, approve={approve_scope}"

                # Target consistency check (if present)
                if "target" in submit_payload or "target" in payload:
                    submit_target = submit_payload.get("target")
                    approve_target = payload.get("target")

                    if submit_target != approve_target:
                        return False, f"target mismatch: submit={submit_target}, approve={approve_target}"

        except Exception as e:
            # If scope/target check fails, it's a validation error (don't block entirely)
            # But this should be rare; return error
            return False, f"scope/target validation error: {str(e)[:100]}"

    return True, None


def enrich_payload_for_cli_approve(actor_identity: str, scope: list,
                                    authority_role: str, note: Optional[str] = None) -> Dict[str, Any]:
    """
    Build payload dict for CLI approve() action.

    Args:
        actor_identity: TTY-provided actor name (e.g., 'kimura_phd')
        scope: Scope of approval (e.g., ['component_A'])
        authority_role: Authority role (e.g., 'HG_AUTHORITY_HOLDER_CLI')
        note: Optional approval rationale

    Returns:
        payload dict ready for approve()
    """
    payload = {
        "actor": actor_identity,
        "scope": scope,
        "authority_role": authority_role,
    }
    if note:
        payload["note"] = note
    return payload


def payload_to_authorization_state_input(
    payload: Dict[str, Any],
    event_id: str,
    timestamp: str,
    request_id: str,
    next_state: str
) -> Dict[str, Any]:
    """
    Transform human_gate_events approve payload to authorization_state input.

    Args:
        payload: human_gate_events payload (validated)
        event_id: human_gate_events.event_id
        timestamp: human_gate_events.timestamp
        request_id: human_gate_events.request_id
        next_state: human_gate_events.next_state (should be "APPROVED" for issuance)

    Returns:
        dict with fields ready for authorization_state table insertion

    Notes:
        - standing is always set to "UNKNOWN" (HG-AS-01 requirement)
        - status is mapped from next_state
        - hg_event_source references the human_gate event
    """
    if next_state != "APPROVED":
        raise ValueError(f"Only APPROVED events can issue authorization state; got {next_state}")

    import uuid

    return {
        "authorization_id": str(uuid.uuid4()),
        "decision_id": payload.get("decision_id"),  # nullable
        "subject": payload.get("actor"),
        "scope": json.dumps(payload.get("scope", [])),  # JSON array as string
        "standing": "UNKNOWN",  # HG-AS-01: explicit UNKNOWN
        "status": "APPROVED",  # mapped from next_state="APPROVED"
        "granted_by": payload.get("authority_role"),
        "granted_at": timestamp,
        "expires_at": payload.get("expires_at"),  # nullable
        "evidence": json.dumps({"source": payload.get("evidence_ref", [])}) if payload.get("evidence_ref") else None,
        "hg_event_source": event_id,
        "hg_event_timestamp": timestamp,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "immutable": 1,  # always immutable on creation
    }


if __name__ == "__main__":
    # Test examples
    print("=== HG-AS-01 Payload Schema Validation Tests ===\n")

    # Valid payload
    valid_payload = {
        "actor": "kimura_phd",
        "scope": ["component_A", "component_J"],
        "authority_role": "HG_AUTHORITY_HOLDER_01",
        "decision_id": "DC_20260918_001",
        "expires_at": "2026-10-22T00:00:00Z",
        "evidence_ref": ["PAPER5_PHASE2_20260918"],
        "note": "Approval rationale"
    }
    is_valid, err = validate_payload_for_approve(valid_payload)
    print(f"Valid payload: {is_valid}")
    if err:
        print(f"  Error: {err}")

    # Missing mandatory field
    invalid_payload_1 = {
        "actor": "kimura_phd",
        "scope": ["component_A"],
    }
    is_valid, err = validate_payload_for_approve(invalid_payload_1)
    print(f"\nMissing authority_role: {is_valid}")
    print(f"  Error: {err}")

    # Empty actor
    invalid_payload_2 = {
        "actor": "",
        "scope": ["component_A"],
        "authority_role": "HG_AUTHORITY_HOLDER_01",
    }
    is_valid, err = validate_payload_for_approve(invalid_payload_2)
    print(f"\nEmpty actor: {is_valid}")
    print(f"  Error: {err}")
