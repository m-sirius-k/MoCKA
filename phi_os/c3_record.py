#!/usr/bin/env python3
"""
C3 Canonical Record Adapter (R02 Institutional Memory Foundation)

Maps C3 authorization execution to institutional event records.
Enables third-party reconstruction of: Decision → Authority → Runtime → Consequence

Minimum contract for R02 reconstructability:
- record_id: unique event_id
- record_type: "c3_authorization_execution"
- canonicality: "CANONICAL" | "UNKNOWN" | "MISSING"
- when_ts: timestamp
- who_actor: requesting identity
- decision_id: institutional decision (if known)
- auth_request_id: Human Gate auth ID
- endpoint_route: /decision/approve | /decision/reject | /api/action/publish_all | /api/distribution/publish | /public/write_event
- trace_id: joinable trace for reconstruction
- state_before: authorization state before execution (APPROVED, PENDING, etc.)
- authorization_scope: C3-007 scope binding
- target: C3-008 target binding (or "NOT_APPLICABLE" for /public/write_event)
- action: C3-008 action binding (or "NOT_APPLICABLE" for /public/write_event)
- consume_result: "SUCCESS" | "EXCEPTION" | "UNKNOWN"
- consume_exception_code: C3_CONSUME_FAILED | C3_AUTHZ_EXPIRED | etc. (if failed)
- effect_result: "SUCCESS" | "EXCEPTION" | "UNKNOWN"
- outcome: HTTP response code (200, 403, 500)
- evidence_refs: [git_sha, related_event_ids]
- implementation_sha: git commit SHA where this C3 level was implemented
- parent_record_id: previous step in authorization sequence

All fields must be explicitly present. Missing values use:
- "MISSING" when configured but not provided at runtime
- "UNKNOWN" when not yet determined
- "NOT_APPLICABLE" when intentionally excluded by Human Decision
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Import from parent module
import sys
_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root))

# C3 Implementation SHAs (update as new C3 levels are added)
C3_IMPLEMENTATION_SHAS = {
    "C3-005": "86945ce",  # State validation
    "C3-006": "2d7f356",  # Expiry checking
    "C3-007": "86945ce",  # Scope binding
    "C3-008": "54d5fc9",  # Target+Action binding
    "C3-009": "51a7a37",  # PRE-CONSUME (4 endpoints)
    "C3-010": "aa47f03",  # PRE-CONSUME (/public/write_event)
}

class C3CanonicalRecord:
    """Represents one step in C3 authorization execution for institutional memory."""

    def __init__(
        self,
        endpoint_route: str,
        auth_request_id: str,
        trace_id: str,
        state_before: str = "UNKNOWN",
        authorization_scope: str = "UNKNOWN",
        target: Optional[str] = None,
        action: Optional[str] = None,
        consume_result: str = "UNKNOWN",
        consume_exception_code: Optional[str] = None,
        effect_result: str = "UNKNOWN",
        outcome: int = 0,
        who_actor: str = "UNKNOWN",
        decision_id: Optional[str] = None,
        parent_record_id: Optional[str] = None,
    ):
        """Initialize canonical record."""
        self.record_id = f"C3R_{uuid.uuid4().hex[:16].upper()}"
        self.record_type = "c3_authorization_execution"
        self.canonicality = "CANONICAL"  # Explicitly declare this is institutional
        self.when_ts = datetime.now(timezone.utc).isoformat()
        self.who_actor = who_actor
        self.endpoint_route = endpoint_route
        self.auth_request_id = auth_request_id
        self.trace_id = trace_id
        self.decision_id = decision_id or "UNKNOWN"
        self.state_before = state_before
        self.authorization_scope = authorization_scope
        self.target = target or "NOT_APPLICABLE"  # Only applicable for C3-008 endpoints
        self.action = action or "NOT_APPLICABLE"  # Only applicable for C3-008 endpoints
        self.consume_result = consume_result
        self.consume_exception_code = consume_exception_code or "NONE"
        self.effect_result = effect_result
        self.outcome = outcome
        self.parent_record_id = parent_record_id or "NONE"

        # Determine C3 level from endpoint
        self.c3_levels = self._determine_c3_levels()
        self.implementation_sha = C3_IMPLEMENTATION_SHAS.get(self.c3_levels[-1], "UNKNOWN")

    def _determine_c3_levels(self) -> List[str]:
        """Determine which C3 levels apply to this endpoint."""
        # All protected endpoints have C3-005, C3-006, C3-007
        levels = ["C3-005", "C3-006", "C3-007"]

        # C3-008 (target/action binding) on 4 endpoints only
        if self.endpoint_route in [
            "/decision/approve",
            "/decision/reject",
            "/api/action/publish_all",
            "/api/distribution/publish",
        ]:
            levels.append("C3-008")

        # C3-009 or C3-010 (PRE-CONSUME) on all protected endpoints
        if self.endpoint_route == "/public/write_event":
            levels.append("C3-010")
        else:
            levels.append("C3-009")

        return levels

    def to_event_record(self) -> Dict:
        """Convert to app.py append_event() compatible record."""
        c3_json = {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "canonicality": self.canonicality,
            "endpoint_route": self.endpoint_route,
            "auth_request_id": self.auth_request_id,
            "trace_id": self.trace_id,
            "decision_id": self.decision_id,
            "state_before": self.state_before,
            "authorization_scope": self.authorization_scope,
            "target": self.target,
            "action": self.action,
            "consume_result": self.consume_result,
            "consume_exception_code": self.consume_exception_code,
            "effect_result": self.effect_result,
            "outcome": self.outcome,
            "implementation_sha": self.implementation_sha,
            "c3_levels": self.c3_levels,
            "parent_record_id": self.parent_record_id,
        }

        return {
            "event_id": self.record_id,
            "when": self.when_ts,
            "who_actor": self.who_actor,
            "what_type": self.record_type,
            "where_component": "human_gate",
            "where_path": self.endpoint_route,
            "why_purpose": f"C3 Authorization Boundary Enforcement",
            "how_trigger": "endpoint_execution",
            "channel_type": "api",
            "lifecycle_phase": "in_operation",
            "risk_level": "normal",
            "category_ab": self.c3_levels[0].split("-")[1],  # Extract 005/006/007/008/009/010
            "target_class": "authorization_boundary",
            "title": f"[C3-EXECUTION] {self.endpoint_route} auth_id={self.auth_request_id}",
            "short_summary": f"Execution: {self.endpoint_route} consume={self.consume_result} effect={self.effect_result} outcome={self.outcome}",
            "before_state": self.state_before,
            "after_state": f"consume={self.consume_result}",
            "change_type": "authorization_state_transition",
            "impact_scope": "authorization",
            "impact_result": f"HTTP {self.outcome}",
            "related_event_id": self.parent_record_id if self.parent_record_id != "NONE" else "NONE",
            "trace_id": self.trace_id,
            "free_note": json.dumps(c3_json, ensure_ascii=False),
        }

    def __repr__(self):
        return f"C3Record(id={self.record_id}, endpoint={self.endpoint_route}, auth={self.auth_request_id}, consume={self.consume_result}, effect={self.effect_result}, outcome={self.outcome})"


def create_c3_record(
    endpoint_route: str,
    auth_request_id: str,
    trace_id: str,
    state_before: str = "UNKNOWN",
    authorization_scope: str = "UNKNOWN",
    target: Optional[str] = None,
    action: Optional[str] = None,
    consume_result: str = "UNKNOWN",
    consume_exception_code: Optional[str] = None,
    effect_result: str = "UNKNOWN",
    outcome: int = 0,
    who_actor: str = "UNKNOWN",
    decision_id: Optional[str] = None,
    parent_record_id: Optional[str] = None,
) -> C3CanonicalRecord:
    """Factory function to create a C3 canonical record."""
    return C3CanonicalRecord(
        endpoint_route=endpoint_route,
        auth_request_id=auth_request_id,
        trace_id=trace_id,
        state_before=state_before,
        authorization_scope=authorization_scope,
        target=target,
        action=action,
        consume_result=consume_result,
        consume_exception_code=consume_exception_code,
        effect_result=effect_result,
        outcome=outcome,
        who_actor=who_actor,
        decision_id=decision_id,
        parent_record_id=parent_record_id,
    )


def record_c3_execution(
    record: C3CanonicalRecord,
    append_event_func,
) -> bool:
    """Persist C3 canonical record to institutional event stream via append_event()."""
    try:
        event_record = record.to_event_record()
        append_event_func(event_record)
        return True
    except Exception as e:
        print(f"[C3-RECORD] Failed to persist: {e}")
        return False
