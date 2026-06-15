"""Decision Engine.

Final, centralized integration stage of the pipeline. Takes the
outputs of Validation, Compliance and Policy Engines and produces the
single DecisionRecord that Runtime is allowed to act on.

Design choice (fully centralized): no other engine and no Runtime
component may emit a pass/fail verdict. Only DecisionRecord.decision
is authoritative. This keeps the decision logic in one place and
makes the audit trail unambiguous (one record == one verdict).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from ..contracts.compliance_contract import ComplianceLevel, ComplianceRecord
from ..contracts.policy_contract import PolicyEvaluation, PolicyResult
from ..contracts.validation_contract import ValidationRecord, ValidationResult


class DecisionResult(str, Enum):
    """Final verdict handed to Runtime."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


_BLOCKING_VALIDATION = {ValidationResult.INVALID}
_BLOCKING_COMPLIANCE = {ComplianceLevel.NON_COMPLIANT}
_BLOCKING_POLICY = {PolicyResult.FAIL}

_WARNING_VALIDATION = {ValidationResult.WARNING}
_WARNING_COMPLIANCE = {ComplianceLevel.PARTIALLY_COMPLIANT}
_WARNING_POLICY = {PolicyResult.WARNING}


@dataclass(frozen=True)
class DecisionRecord:
    """The single, authoritative output of the Governance pipeline."""

    module_id: str
    module_version: str
    decision: DecisionResult
    reasons: Sequence[str] = field(default_factory=tuple)
    validation_id: str = ""
    compliance_id: str = ""
    policy_ids: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.module_id:
            raise ValueError("DecisionRecord.module_id is required")
        if not self.module_version:
            raise ValueError("DecisionRecord.module_version is required")
        if not isinstance(self.decision, DecisionResult):
            raise ValueError("DecisionRecord.decision must be a DecisionResult")


def run_decision(
    validation_record: ValidationRecord,
    compliance_record: ComplianceRecord,
    policy_evaluations: Sequence[PolicyEvaluation],
) -> DecisionRecord:
    """Aggregate Validation/Compliance/Policy outputs into one verdict.

    Precedence: any blocking result -> FAIL, else any warning -> WARNING,
    else PASS. Reasons list every contributing non-PASS finding so the
    Decision Record is self-explanatory for Audit.
    """

    reasons: list[str] = []
    blocking = False
    warning = False

    if validation_record.result in _BLOCKING_VALIDATION:
        blocking = True
        reasons.append(f"validation={validation_record.result.value}")
    elif validation_record.result in _WARNING_VALIDATION:
        warning = True
        reasons.append(f"validation={validation_record.result.value}")

    if compliance_record.level in _BLOCKING_COMPLIANCE:
        blocking = True
        reasons.append(f"compliance={compliance_record.level.value}")
    elif compliance_record.level in _WARNING_COMPLIANCE:
        warning = True
        reasons.append(f"compliance={compliance_record.level.value}")

    for pe in policy_evaluations:
        if pe.result in _BLOCKING_POLICY:
            blocking = True
            reasons.append(f"policy[{pe.category}]={pe.result.value}")
        elif pe.result in _WARNING_POLICY:
            warning = True
            reasons.append(f"policy[{pe.category}]={pe.result.value}")

    if blocking:
        decision = DecisionResult.FAIL
    elif warning:
        decision = DecisionResult.WARNING
    else:
        decision = DecisionResult.PASS

    return DecisionRecord(
        module_id=validation_record.module_id,
        module_version=validation_record.module_version,
        decision=decision,
        reasons=tuple(reasons),
        validation_id=validation_record.validation_id,
        compliance_id=compliance_record.compliance_id,
        policy_ids=tuple(pe.policy_id for pe in policy_evaluations),
    )
