"""Unit tests for engines.decision_engine.

Reference: "Decision Engine" precedence rules established in Phase 2
(FAIL > WARNING > PASS), all other engines produce status only.
"""

from core_kernel.governance.contracts.compliance_contract import ComplianceLevel
from core_kernel.governance.engines.compliance_engine import run_compliance
from core_kernel.governance.engines.decision_engine import DecisionResult, run_decision
from core_kernel.governance.engines.policy_engine import run_policy
from core_kernel.governance.engines.validation_engine import run_validation


def _records(timestamp, evidence, domain_evidence, category_evidence):
    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, evidence)
    cr = run_compliance("COMP-1", vr, timestamp, domain_evidence)
    pes = run_policy("mod.x", timestamp, category_evidence)
    return vr, cr, pes


def test_all_pass_yields_pass(timestamp, full_validation_evidence):
    vr, cr, pes = _records(timestamp, full_validation_evidence, {}, {})
    decision = run_decision(vr, cr, pes)
    assert decision.decision is DecisionResult.PASS
    assert decision.reasons == ()


def test_warning_anywhere_yields_warning_not_fail(timestamp, full_validation_evidence):
    vr, cr, pes = _records(
        timestamp, full_validation_evidence, {}, {"Security Policy": {"result": "WARNING"}}
    )
    decision = run_decision(vr, cr, pes)
    assert decision.decision is DecisionResult.WARNING
    assert any("Security Policy" in r for r in decision.reasons)


def test_policy_fail_yields_fail_even_with_valid_validation(timestamp, full_validation_evidence):
    vr, cr, pes = _records(
        timestamp, full_validation_evidence, {}, {"Security Policy": {"result": "FAIL"}}
    )
    decision = run_decision(vr, cr, pes)
    assert decision.decision is DecisionResult.FAIL


def test_invalid_validation_dominates_warning(timestamp, full_validation_evidence):
    evidence = dict(full_validation_evidence)
    evidence["Documentation"] = False  # -> INVALID -> NON_COMPLIANT
    vr, cr, pes = _records(
        timestamp, evidence, {}, {"Security Policy": {"result": "WARNING"}}
    )
    assert cr.level is ComplianceLevel.NON_COMPLIANT
    decision = run_decision(vr, cr, pes)
    assert decision.decision is DecisionResult.FAIL
    assert len(decision.reasons) >= 2  # validation + compliance


def test_decision_record_carries_traceability_ids(timestamp, full_validation_evidence):
    vr, cr, pes = _records(timestamp, full_validation_evidence, {}, {})
    decision = run_decision(vr, cr, pes)
    assert decision.validation_id == vr.validation_id
    assert decision.compliance_id == cr.compliance_id
    assert decision.policy_ids == tuple(p.policy_id for p in pes)
    assert decision.module_id == "mod.x"
    assert decision.module_version == "1.0.0"
