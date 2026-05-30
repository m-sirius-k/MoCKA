"""
vasAI Core: Auto-Gate + Human Gate 統合ガバナンス。
"""
import threading
from datetime import datetime, timezone
from typing import Optional

from core import event_store
from core.models import Decision, DecisionStatus, RiskLevel

_lock = threading.Lock()
_pending: dict[str, Decision] = {}


def assess_risk(event: dict) -> RiskLevel:
    what = event.get("what_type", "")
    content = event.get("content", {})
    risk_hint = content.get("risk_level", "")

    if risk_hint == "CRITICAL" or what in ("CRITICAL_ALERT", "SYSTEM_HALT"):
        return RiskLevel.CRITICAL
    if risk_hint == "HIGH" or what in ("INCIDENT", "SECURITY_BREACH"):
        return RiskLevel.HIGH
    if risk_hint == "CAUTION" or what in ("WARNING", "ANOMALY"):
        return RiskLevel.CAUTION
    return RiskLevel.NORMAL


def create_decision(event_id: str, risk_level: RiskLevel) -> Decision:
    d = Decision(event_id=event_id, risk_level=risk_level)
    with _lock:
        _pending[d.decision_id] = d
    return d


def auto_approve(decision: Decision) -> Decision:
    if decision.risk_level not in (RiskLevel.NORMAL, RiskLevel.CAUTION):
        raise ValueError(f"Cannot auto-approve risk level: {decision.risk_level}")
    updated = decision.model_copy(update={
        "status":     DecisionStatus.AUTO_APPROVED,
        "decided_by": "AUTO_GATE",
        "decided_at": datetime.now(timezone.utc),
        "reason":     f"Auto-approved: {decision.risk_level.value}",
    })
    with _lock:
        _pending.pop(decision.decision_id, None)
    event_store.append(
        who_actor="vasAI.governance",
        what_type="DECISION_AUTO_APPROVED",
        why_purpose="Auto-Gate承認",
        content={"decision_id": updated.decision_id, "risk": updated.risk_level.value},
        stage="DECISION",
    )
    return updated


def queue_for_human(decision: Decision) -> Decision:
    updated = decision.model_copy(update={"status": DecisionStatus.PENDING})
    with _lock:
        _pending[updated.decision_id] = updated
    event_store.append(
        who_actor="vasAI.governance",
        what_type="DECISION_PENDING_HUMAN",
        why_purpose="Human Gate待機",
        content={"decision_id": updated.decision_id, "risk": updated.risk_level.value},
        stage="DECISION",
    )
    return updated


def approve(decision_id: str, reason: str = "", approver: str = "HUMAN") -> Decision:
    with _lock:
        d = _pending.get(decision_id)
    if d is None:
        raise KeyError(f"Decision not found: {decision_id}")
    updated = d.model_copy(update={
        "status":     DecisionStatus.APPROVED,
        "decided_by": approver,
        "decided_at": datetime.now(timezone.utc),
        "reason":     reason,
    })
    with _lock:
        _pending.pop(decision_id, None)
    event_store.append(
        who_actor=approver,
        what_type="DECISION_APPROVED",
        why_purpose=reason,
        content={"decision_id": decision_id},
        stage="DECISION",
    )
    return updated


def reject(decision_id: str, reason: str = "", approver: str = "HUMAN") -> Decision:
    with _lock:
        d = _pending.get(decision_id)
    if d is None:
        raise KeyError(f"Decision not found: {decision_id}")
    updated = d.model_copy(update={
        "status":     DecisionStatus.REJECTED,
        "decided_by": approver,
        "decided_at": datetime.now(timezone.utc),
        "reason":     reason,
    })
    with _lock:
        _pending.pop(decision_id, None)
    event_store.append(
        who_actor=approver,
        what_type="DECISION_REJECTED",
        why_purpose=reason,
        content={"decision_id": decision_id},
        stage="DECISION",
    )
    return updated


def auto_reject_critical(decision: Decision) -> Decision:
    updated = decision.model_copy(update={
        "status":     DecisionStatus.REJECTED,
        "decided_by": "AUTO_GATE_CRITICAL",
        "decided_at": datetime.now(timezone.utc),
        "reason":     "CRITICAL risk — auto-rejected and system alerted",
    })
    with _lock:
        _pending.pop(decision.decision_id, None)
    event_store.append(
        who_actor="vasAI.governance",
        what_type="CRITICAL_ALERT",
        why_purpose="CRITICAL risk auto-rejected",
        content={"decision_id": updated.decision_id},
        stage="DECISION",
    )
    return updated


def process(event_id: str, event: dict) -> Decision:
    risk = assess_risk(event)
    decision = create_decision(event_id, risk)

    if risk == RiskLevel.CRITICAL:
        return auto_reject_critical(decision)
    if risk in (RiskLevel.NORMAL, RiskLevel.CAUTION):
        return auto_approve(decision)
    return queue_for_human(decision)


def get_pending() -> list[Decision]:
    with _lock:
        return list(_pending.values())
