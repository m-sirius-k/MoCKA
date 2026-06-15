"""Event Pipeline.

Flow control only. Calls Engines in the fixed order
(Validation -> Compliance -> Policy -> Decision) and threads their
outputs through unchanged. No judgement is made here — every verdict
originates from the Engines, the final one always from Decision Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..contracts.compliance_contract import ComplianceRecord
from ..contracts.policy_contract import PolicyEvaluation
from ..contracts.validation_contract import ValidationRecord
from ..engines.compliance_engine import run_compliance
from ..engines.decision_engine import DecisionRecord, run_decision
from ..engines.policy_engine import run_policy
from ..engines.validation_engine import run_validation


@dataclass(frozen=True)
class GovernanceEvent:
    """Input to the Governance pipeline.

    This is the Runtime-side input shape. It carries the raw evidence
    each Engine needs; the pipeline does not interpret it beyond
    passing it through to the corresponding Engine.
    """

    event_id: str
    module_id: str
    module_version: str
    timestamp: str
    validation_evidence: Mapping[str, Any] = field(default_factory=dict)
    compliance_domain_evidence: Mapping[str, Any] = field(default_factory=dict)
    policy_category_evidence: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("GovernanceEvent.event_id is required")
        if not self.module_id:
            raise ValueError("GovernanceEvent.module_id is required")
        if not self.module_version:
            raise ValueError("GovernanceEvent.module_version is required")
        if not self.timestamp:
            raise ValueError("GovernanceEvent.timestamp is required (ISO8601)")


@dataclass(frozen=True)
class PipelineResult:
    """Every intermediate Contract produced while processing one Event."""

    event: GovernanceEvent
    validation_record: ValidationRecord
    compliance_record: ComplianceRecord
    policy_evaluations: tuple[PolicyEvaluation, ...]
    decision_record: DecisionRecord


def run_pipeline(event: GovernanceEvent) -> PipelineResult:
    """Run the fixed Engine chain for ``event``.

    Validation -> Compliance -> Policy -> Decision.
    Pure: depends only on ``event`` and the Engine functions.
    """

    validation_record = run_validation(
        validation_id=f"VAL-{event.event_id}",
        module_id=event.module_id,
        module_version=event.module_version,
        timestamp=event.timestamp,
        evidence=event.validation_evidence,
    )

    compliance_record = run_compliance(
        compliance_id=f"COMP-{event.event_id}",
        validation_record=validation_record,
        assessment_date=event.timestamp,
        domain_evidence=event.compliance_domain_evidence,
    )

    policy_evaluations = run_policy(
        module_id=event.module_id,
        timestamp=event.timestamp,
        category_evidence=event.policy_category_evidence,
    )

    decision_record = run_decision(
        validation_record=validation_record,
        compliance_record=compliance_record,
        policy_evaluations=policy_evaluations,
    )

    return PipelineResult(
        event=event,
        validation_record=validation_record,
        compliance_record=compliance_record,
        policy_evaluations=policy_evaluations,
        decision_record=decision_record,
    )
