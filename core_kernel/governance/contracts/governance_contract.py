"""Governance Contract.

Reference: docs/governance/MODULE_GOVERNANCE_RUNTIME_v1.md
Defines the Governance Runtime Record that ties the standard
runtime workflow (Section 3) together with references to the
Policy / Validation / Compliance contracts produced along the way.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from .compliance_contract import ComplianceRecord
from .event_contract import EventContract
from .policy_contract import PolicyEvaluation
from .validation_contract import ValidationRecord

CONTRACT_VERSION = "1.0.0"


class RuntimeStage(str, Enum):
    """MODULE_GOVERNANCE_RUNTIME_v1 Section 3: Runtime Workflow."""

    REGISTRATION = "Module Registration"
    POLICY_EVALUATION = "Policy Evaluation"
    RULE_EVALUATION = "Rule Evaluation"
    VALIDATION = "Validation"
    COMPLIANCE_ASSESSMENT = "Compliance Assessment"
    AUDIT = "Audit"
    CERTIFICATION = "Certification"
    REGISTRY_UPDATE = "Registry Update"
    RUNTIME_AVAILABILITY = "Runtime Availability"


RUNTIME_STAGE_ORDER: Sequence[RuntimeStage] = tuple(RuntimeStage)


@dataclass(frozen=True)
class GovernanceRuntimeRecord:
    """A single run of the Governance Runtime workflow for one module."""

    module_id: str
    module_version: str
    stage: RuntimeStage
    policy_evaluations: Sequence[PolicyEvaluation] = field(default_factory=tuple)
    validation_record: ValidationRecord | None = None
    compliance_record: ComplianceRecord | None = None
    event_reference: EventContract | None = None

    def __post_init__(self) -> None:
        if not self.module_id:
            raise ValueError("GovernanceRuntimeRecord.module_id is required")
        if not self.module_version:
            raise ValueError("GovernanceRuntimeRecord.module_version is required")
        if not isinstance(self.stage, RuntimeStage):
            raise ValueError("GovernanceRuntimeRecord.stage must be a RuntimeStage")
