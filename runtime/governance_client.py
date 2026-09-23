"""
Governance system client interface (stub for MVP).
For now, returns synthetic governance decision.
In production, this calls actual governance evaluation system.
"""
import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate(plan):
    """
    Submit plan to governance system for evaluation.
    Returns: {
        "decision_record_id": str (UUID),
        "governance_decision": str (PASS | WARNING | FAIL),
        "governance_reason": str (optional),
        "timestamp": str (ISO8601)
    }

    For MVP: Always returns PASS (stub behavior).
    In production: Call actual governance service.
    """
    plan_id = plan.get("plan_id", "UNKNOWN")
    intent_id = plan.get("intent_id", "UNKNOWN")
    steps = plan.get("steps", [])

    decision_record_id = str(uuid.uuid4())

    decision = "PASS"
    reason = f"Plan {plan_id} passed governance check (stub)"

    return {
        "decision_record_id": decision_record_id,
        "governance_decision": decision,
        "governance_reason": reason,
        "timestamp": _now()
    }
