"""Decision Rationale.

Turns a PipelineResult (Phase 3) into a reasoned explanation of *why*
the Decision Engine produced its verdict, citing the Validation,
Compliance and Policy records that fed it. Does not recompute the
Decision — DecisionRecord.decision and .reasons remain authoritative;
this module only narrates them.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..engines.decision_engine import DecisionResult
from ..runtime.event_pipeline import PipelineResult


@dataclass(frozen=True)
class RationaleRecord:
    event_id: str
    module_id: str
    module_version: str
    decision: DecisionResult
    summary: str
    contributing_factors: tuple[str, ...]


def _factor_for_validation(pipeline: PipelineResult) -> str | None:
    vr = pipeline.validation_record
    if vr.result.value == "VALID":
        return None
    return f"Validation={vr.result.value} ({vr.notes or 'see ValidationRecord.evidence'})"


def _factor_for_compliance(pipeline: PipelineResult) -> str | None:
    cr = pipeline.compliance_record
    if cr.level.value in ("COMPLIANT", "FULLY_COMPLIANT"):
        return None
    non_passing = {k: v for k, v in cr.findings.items() if v not in ("PASS", "VALID", "NOT_APPLICABLE")}
    return f"Compliance={cr.level.value} (domains: {non_passing})"


def _factors_for_policy(pipeline: PipelineResult) -> list[str]:
    factors = []
    for pe in pipeline.policy_evaluations:
        if pe.result.value not in ("PASS", "NOT_APPLICABLE"):
            factors.append(f"Policy[{pe.category}]={pe.result.value}: {pe.evaluation_criteria}")
    return factors


def build_rationale(pipeline: PipelineResult) -> RationaleRecord:
    decision = pipeline.decision_record.decision

    factors: list[str] = []
    for f in (_factor_for_validation(pipeline), _factor_for_compliance(pipeline)):
        if f:
            factors.append(f)
    factors.extend(_factors_for_policy(pipeline))

    if decision is DecisionResult.PASS:
        summary = (
            f"{pipeline.event.module_id}@{pipeline.event.module_version}: "
            "PASS - Validation, Compliance and all evaluated Policies are "
            "within bounds; Runtime committed."
        )
    elif decision is DecisionResult.WARNING:
        summary = (
            f"{pipeline.event.module_id}@{pipeline.event.module_version}: "
            f"WARNING - committed, but {len(factors)} factor(s) need attention: "
            + "; ".join(factors)
        )
    else:
        summary = (
            f"{pipeline.event.module_id}@{pipeline.event.module_version}: "
            f"FAIL - blocked due to {len(factors)} blocking/warning factor(s): "
            + "; ".join(factors)
        )

    return RationaleRecord(
        event_id=pipeline.event.event_id,
        module_id=pipeline.event.module_id,
        module_version=pipeline.event.module_version,
        decision=decision,
        summary=summary,
        contributing_factors=tuple(factors),
    )
