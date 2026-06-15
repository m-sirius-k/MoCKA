"""Governance Runtime.

Orchestration only. GovernanceRuntime never re-evaluates, scores, or
re-applies rules — it runs the fixed Engine chain via
``event_pipeline.run_pipeline``, executes the single DecisionRecord it
receives (commit or block — nothing in between), and forwards every
stage to an Audit sink.

Runtime responsibilities (fixed):
    - Event reception
    - Engine invocation (fixed order, via event_pipeline)
    - Decision reception
    - Commit execution
    - Audit forwarding
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from ..engines.decision_engine import DecisionResult
from .event_pipeline import GovernanceEvent, PipelineResult, run_pipeline


class AuditSink(Protocol):
    """Audit-layer interface. Runtime depends on this Protocol only —
    not on any concrete Audit implementation (Phase 4)."""

    def record(self, event_id: str, stage: str, payload: Mapping[str, Any]) -> None:
        ...


class _NullAuditSink:
    """Default sink used until Phase 4 wires a real Audit Logger."""

    def record(self, event_id: str, stage: str, payload: Mapping[str, Any]) -> None:
        return None


@dataclass(frozen=True)
class CommitRecord:
    """Result of executing a DecisionRecord. Runtime only executes what
    Decision Engine already decided; ``committed`` mirrors
    ``decision != FAIL`` and is not a separate judgement."""

    event_id: str
    module_id: str
    module_version: str
    decision: DecisionResult
    committed: bool


@dataclass(frozen=True)
class ExecutionResult:
    """Full Event -> Commit trace for one GovernanceEvent."""

    pipeline: PipelineResult
    commit: CommitRecord


_AUDIT_STAGES = (
    "validation",
    "compliance",
    "policy",
    "decision",
    "commit",
)


@dataclass
class GovernanceRuntime:
    """Fixed orchestration: Event -> Engines -> Decision -> Commit -> Audit."""

    audit_sink: AuditSink = field(default_factory=_NullAuditSink)

    def execute(self, event: GovernanceEvent) -> ExecutionResult:
        pipeline = run_pipeline(event)
        decision = pipeline.decision_record.decision

        commit = CommitRecord(
            event_id=event.event_id,
            module_id=pipeline.decision_record.module_id,
            module_version=pipeline.decision_record.module_version,
            decision=decision,
            committed=decision != DecisionResult.FAIL,
        )

        self._forward_to_audit(pipeline, commit)

        return ExecutionResult(pipeline=pipeline, commit=commit)

    def _forward_to_audit(self, pipeline: PipelineResult, commit: CommitRecord) -> None:
        event_id = pipeline.event.event_id
        self.audit_sink.record(event_id, "validation", {"record": pipeline.validation_record})
        self.audit_sink.record(event_id, "compliance", {"record": pipeline.compliance_record})
        self.audit_sink.record(event_id, "policy", {"records": pipeline.policy_evaluations})
        timestamp = pipeline.event.timestamp
        self.audit_sink.record(
            event_id, "decision", {"record": pipeline.decision_record, "timestamp": timestamp}
        )
        self.audit_sink.record(event_id, "commit", {"record": commit, "timestamp": timestamp})
