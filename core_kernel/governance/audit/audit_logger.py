"""Audit Logger.

Implements the ``AuditSink`` Protocol consumed by
``runtime.governance_runtime.GovernanceRuntime``. For each stage
forwarded by Runtime, restructures the already-decided record into one
or more ``AuditRecord`` entries and appends them to an ``AuditStore``.

Strictly observation: no recomputation, no new decisions, no
overriding of the values Runtime/Engines already produced.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..contracts.compliance_contract import CONTRACT_VERSION as COMPLIANCE_CONTRACT_VERSION
from ..contracts.governance_contract import CONTRACT_VERSION as GOVERNANCE_CONTRACT_VERSION
from ..contracts.policy_contract import CONTRACT_VERSION as POLICY_CONTRACT_VERSION
from ..contracts.validation_contract import CONTRACT_VERSION as VALIDATION_CONTRACT_VERSION
from .audit_schema import AuditRecord
from .audit_store import AuditStore


class AuditLogger:
    """AuditSink implementation backed by an AuditStore."""

    def __init__(self, store: AuditStore) -> None:
        self._store = store

    def record(self, event_id: str, stage: str, payload: Mapping[str, Any]) -> None:
        for audit_record in self._to_audit_records(event_id, stage, payload):
            self._store.append(audit_record)

    def _to_audit_records(
        self, event_id: str, stage: str, payload: Mapping[str, Any]
    ) -> list[AuditRecord]:
        if stage == "validation":
            r = payload["record"]
            return [
                AuditRecord(
                    event_id=event_id,
                    engine="ValidationEngine",
                    rule=r.validation_id,
                    decision=r.result.value,
                    reason=r.notes,
                    timestamp=r.validation_timestamp,
                    version=VALIDATION_CONTRACT_VERSION,
                )
            ]

        if stage == "compliance":
            r = payload["record"]
            return [
                AuditRecord(
                    event_id=event_id,
                    engine="ComplianceEngine",
                    rule=r.compliance_id,
                    decision=r.level.value,
                    reason=str(r.findings),
                    timestamp=r.assessment_date,
                    version=COMPLIANCE_CONTRACT_VERSION,
                )
            ]

        if stage == "policy":
            return [
                AuditRecord(
                    event_id=event_id,
                    engine="PolicyEngine",
                    rule=f"{pe.category}:{pe.policy_id}",
                    decision=pe.result.value,
                    reason=pe.evaluation_criteria,
                    timestamp=pe.timestamp,
                    version=POLICY_CONTRACT_VERSION,
                )
                for pe in payload["records"]
            ]

        if stage == "decision":
            r = payload["record"]
            return [
                AuditRecord(
                    event_id=event_id,
                    engine="DecisionEngine",
                    rule=f"{r.validation_id}|{r.compliance_id}|{','.join(r.policy_ids)}",
                    decision=r.decision.value,
                    reason="; ".join(r.reasons) if r.reasons else "no findings",
                    timestamp=payload["timestamp"],
                    version=GOVERNANCE_CONTRACT_VERSION,
                )
            ]

        if stage == "commit":
            r = payload["record"]
            return [
                AuditRecord(
                    event_id=event_id,
                    engine="GovernanceRuntime",
                    rule="commit",
                    decision="COMMITTED" if r.committed else "BLOCKED",
                    reason=f"decision={r.decision.value}",
                    timestamp=payload["timestamp"],
                    version=GOVERNANCE_CONTRACT_VERSION,
                )
            ]

        raise ValueError(f"Unknown audit stage: {stage!r}")
