"""
vasAI: MoCKAMovement — 第1の心臓。通常運用8ステージループ。
"""
from datetime import datetime, timezone
from typing import Callable, Optional

from core import artifact_schema, audit_chain, event_store, governance
from core.models import (
    ActionResult,
    Artifact,
    AuditReport,
    Decision,
    DecisionStatus,
    MovementStage,
)

_shadow_listeners: list[Callable[[dict], None]] = []


def register_shadow_listener(fn: Callable[[dict], None]) -> None:
    _shadow_listeners.append(fn)


def _emit(event: dict) -> None:
    for fn in _shadow_listeners:
        try:
            fn(event)
        except Exception:
            pass


class MoCKAMovement:
    """第1の心臓。8ステージ完全実装。ShadowMovementがミラーリングする。"""

    def __init__(self, store=None, audit=None, gov=None):
        self._store = store or event_store
        self._audit = audit or audit_chain
        self._gov = gov or governance

    # ── Stage 1: OBSERVATION ──────────────────────────────
    def observe(self, raw_input: dict) -> Artifact:
        artifact = artifact_schema.from_raw(
            raw_input,
            artifact_type=raw_input.get("artifact_type", "message"),
            source_app=raw_input.get("source_app", "vasAI"),
            source_service=raw_input.get("source_service", "default"),
        )
        return artifact

    # ── Stage 2: RECORD ───────────────────────────────────
    def record(self, artifact: Artifact) -> str:
        event_id = self._store.append(
            who_actor=artifact.source_app,
            what_type="ARTIFACT_RECORDED",
            where_component=artifact.source_service,
            why_purpose="MoCKAMovement.record",
            content=artifact_schema.to_event_content(artifact),
            stage=MovementStage.RECORD.value,
        )
        _emit({"stage": MovementStage.RECORD.value, "event_id": event_id,
               "artifact_id": artifact.artifact_id})
        return event_id

    # ── Stage 3: INCIDENT ─────────────────────────────────
    def detect_incident(self, event_id: str) -> bool:
        ev = self._store.get(event_id)
        if ev is None:
            return False
        risk = self._gov.assess_risk(ev)
        from core.models import RiskLevel
        is_incident = risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        if is_incident:
            self._store.append(
                who_actor="vasAI.movement",
                what_type="INCIDENT_DETECTED",
                where_component=ev.get("where_component", ""),
                why_purpose="Incident detected by MoCKAMovement",
                content={"source_event_id": event_id, "risk": risk.value},
                stage=MovementStage.INCIDENT.value,
            )
            _emit({"stage": MovementStage.INCIDENT.value, "event_id": event_id,
                   "risk": risk.value})
        return is_incident

    # ── Stage 4: RECURRENCE ───────────────────────────────
    def check_recurrence(self, pattern: str) -> int:
        events = self._store.list_events(limit=1000, what_type="INCIDENT_DETECTED")
        count = sum(1 for e in events if pattern in str(e.get("content", "")))
        self._store.append(
            who_actor="vasAI.movement",
            what_type="RECURRENCE_CHECK",
            content={"pattern": pattern, "count": count},
            stage=MovementStage.RECURRENCE.value,
        )
        return count

    # ── Stage 5: PREVENTION ───────────────────────────────
    def generate_prevention(self, incident_id: str) -> list[dict]:
        ev = self._store.get(incident_id)
        base = ev.get("content", {}) if ev else {}
        candidates = [
            {"id": f"{incident_id}_P1", "action": "監視強化", "priority": "HIGH",
             "detail": f"関連コンポーネントの監視頻度を2倍に増加"},
            {"id": f"{incident_id}_P2", "action": "承認フロー追加", "priority": "MEDIUM",
             "detail": "同種の操作に Human Gate を追加"},
            {"id": f"{incident_id}_P3", "action": "ドキュメント更新", "priority": "LOW",
             "detail": "インシデント内容を運用手順書に反映"},
        ]
        self._store.append(
            who_actor="vasAI.movement",
            what_type="PREVENTION_GENERATED",
            content={"incident_id": incident_id, "candidates": candidates},
            stage=MovementStage.PREVENTION.value,
        )
        _emit({"stage": MovementStage.PREVENTION.value, "incident_id": incident_id})
        return candidates

    # ── Stage 6: DECISION ─────────────────────────────────
    def decide(self, event_id: str) -> Decision:
        ev = self._store.get(event_id)
        if ev is None:
            raise KeyError(f"Event not found: {event_id}")
        decision = self._gov.process(event_id, ev)
        _emit({"stage": MovementStage.DECISION.value, "decision_id": decision.decision_id,
               "status": decision.status.value})
        return decision

    # ── Stage 7: ACTION ───────────────────────────────────
    def act(self, decision: Decision) -> ActionResult:
        ok = decision.status in (DecisionStatus.APPROVED, DecisionStatus.AUTO_APPROVED)
        msg = "Action executed" if ok else f"Action skipped: {decision.status.value}"
        result = ActionResult(
            decision_id=decision.decision_id,
            success=ok,
            stage=MovementStage.ACTION,
            message=msg,
        )
        self._store.append(
            who_actor="vasAI.movement",
            what_type="ACTION_EXECUTED" if ok else "ACTION_SKIPPED",
            content={"decision_id": decision.decision_id, "success": ok, "message": msg},
            stage=MovementStage.ACTION.value,
        )
        _emit({"stage": MovementStage.ACTION.value, "action_id": result.action_id,
               "success": ok})
        return result

    # ── Stage 8: AUDIT ────────────────────────────────────
    def audit(self) -> AuditReport:
        report = self._audit.verify_chain()
        self._store.append(
            who_actor="vasAI.movement",
            what_type="AUDIT_COMPLETED",
            content={"chain_valid": report.chain_valid,
                     "total_events": report.total_events},
            stage=MovementStage.AUDIT.value,
        )
        _emit({"stage": MovementStage.AUDIT.value, "chain_valid": report.chain_valid})
        return report

    # ── Full 8-stage cycle ────────────────────────────────
    def run_cycle(self, raw_input: dict) -> dict:
        artifact = self.observe(raw_input)
        event_id = self.record(artifact)
        is_incident = self.detect_incident(event_id)
        recurrence_count = 0
        prevention_candidates: list = []
        if is_incident:
            recurrence_count = self.check_recurrence(
                raw_input.get("pattern", event_id)
            )
            prevention_candidates = self.generate_prevention(event_id)
        decision = self.decide(event_id)
        action_result = self.act(decision)
        audit_report = self.audit()

        return {
            "event_id":             event_id,
            "artifact_id":          artifact.artifact_id,
            "is_incident":          is_incident,
            "recurrence_count":     recurrence_count,
            "prevention_count":     len(prevention_candidates),
            "decision_status":      decision.status.value,
            "action_success":       action_result.success,
            "chain_valid":          audit_report.chain_valid,
            "stages_completed":     8,
        }
