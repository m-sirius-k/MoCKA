"""
Execution context: metadata container for T2-T3 governance integration.
Carries intent_id, plan_id, action_id, governance decision, HG decision through entire chain.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutionContext:
    """Holds metadata for entire execution chain: Intent -> Plan -> Governance -> HG -> Execution -> Evidence"""

    # Identity (set by plan generation; immutable in execution_log)
    intent_id: Optional[str] = None
    plan_id: Optional[str] = None
    action_id: Optional[str] = None  # Per-action; format: {intent_id}:{step_index}

    # Governance (set by governance system; immutable in execution_log)
    decision_record_id: Optional[str] = None
    governance_decision: Optional[str] = None  # PASS | WARNING | FAIL
    governance_reason: Optional[str] = None

    # Human Gate (set by HG layer; immutable in execution_log)
    hg_decision: Optional[str] = None  # AUTHORIZED | AUTHORIZED_WITH_CONDITIONS | DENIED
    hg_conditions: list[str] = field(default_factory=list)
    hg_decision_reason: Optional[str] = None
    hg_timestamp: Optional[str] = None

    # Execution (set by execution layer; immutable in execution_log)
    execution_id: Optional[str] = None
    execution_status: Optional[str] = None  # SUCCESS | FAILURE | EXCEPTION | NOT_EXECUTED | BLOCKED
    execution_result: Optional[Any] = None
    execution_timestamp: Optional[str] = None

    # Trace (accumulated during execution; immutable in execution_log)
    trace: list[dict] = field(default_factory=list)

    # Evidence (computed by evidence layer; immutable in execution_log)
    evidence_hash: Optional[str] = None
    evidence_state: Optional[str] = None  # VERIFIED | EVIDENCE_PENDING_RETRY | EVIDENCE_FAILED_PERMANENT
    evidence_reference: Optional[str] = None  # Link to formal_evidence_record (immutable_hash)

    # Institutional Closure (gated by evidence_state per NI-005: A)
    institutional_closure: Optional[str] = None  # CLOSED | BLOCKED | UNRESOLVED

    # Metadata status
    metadata_status: str = "CURRENT"  # CURRENT | LEGACY | UNKNOWN
    metadata_completeness: Optional[dict] = None  # Track which fields are populated

    def is_valid_for_execution(self) -> bool:
        """Check if context has minimum metadata for execution attempt."""
        return bool(self.intent_id and self.plan_id and self.action_id)

    def is_legacy(self) -> bool:
        """Check if context represents legacy plan (missing modern metadata)."""
        return self.metadata_status == "LEGACY"

    def add_trace_event(self, event_type: str, description: str, data: Optional[dict] = None) -> None:
        """Add event to trace log."""
        event = {
            "timestamp": _now(),
            "type": event_type,
            "description": description,
        }
        if data:
            event["data"] = data
        self.trace.append(event)

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "intent_id": self.intent_id,
            "plan_id": self.plan_id,
            "action_id": self.action_id,
            "decision_record_id": self.decision_record_id,
            "governance_decision": self.governance_decision,
            "governance_reason": self.governance_reason,
            "hg_decision": self.hg_decision,
            "hg_conditions": self.hg_conditions,
            "hg_decision_reason": self.hg_decision_reason,
            "hg_timestamp": self.hg_timestamp,
            "execution_id": self.execution_id,
            "execution_status": self.execution_status,
            "execution_result": self.execution_result,
            "execution_timestamp": self.execution_timestamp,
            "trace": self.trace,
            "evidence_hash": self.evidence_hash,
            "metadata_status": self.metadata_status,
        }
