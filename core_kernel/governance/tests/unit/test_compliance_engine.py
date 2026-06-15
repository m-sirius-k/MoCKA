"""Unit tests for engines.compliance_engine.

Reference: docs/governance/MODULE_COMPLIANCE_MODEL_v1.md Sections 3-4.
"""

from core_kernel.governance.contracts.compliance_contract import ComplianceLevel
from core_kernel.governance.contracts.validation_contract import ValidationResult
from core_kernel.governance.engines.compliance_engine import run_compliance
from core_kernel.governance.engines.validation_engine import run_validation


def test_valid_module_with_certified_is_fully_compliant(timestamp, full_validation_evidence):
    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    cr = run_compliance("COMP-1", vr, timestamp, {"Certification": "CERTIFIED"})
    assert cr.level is ComplianceLevel.FULLY_COMPLIANT
    assert cr.findings["Validation"] == ValidationResult.VALID.value


def test_valid_module_without_certification_is_compliant(timestamp, full_validation_evidence):
    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    cr = run_compliance("COMP-2", vr, timestamp, {})
    assert cr.level is ComplianceLevel.COMPLIANT


def test_warning_domain_is_partially_compliant(timestamp, full_validation_evidence):
    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    cr = run_compliance("COMP-3", vr, timestamp, {"Security": "WARNING"})
    assert cr.level is ComplianceLevel.PARTIALLY_COMPLIANT
    assert any("Security" in r for r in cr.recommendations)


def test_failing_domain_or_invalid_validation_is_non_compliant(timestamp, full_validation_evidence):
    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    cr = run_compliance("COMP-4", vr, timestamp, {"Security": "FAIL"})
    assert cr.level is ComplianceLevel.NON_COMPLIANT

    evidence = dict(full_validation_evidence)
    evidence["Documentation"] = False
    vr_invalid = run_validation("VAL-5", "mod.x", "1.0.0", timestamp, evidence)
    cr_invalid = run_compliance("COMP-5", vr_invalid, timestamp, {})
    assert cr_invalid.level is ComplianceLevel.NON_COMPLIANT


def test_unknown_compliance_domain_is_rejected(timestamp, full_validation_evidence):
    import pytest

    vr = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    with pytest.raises(ValueError):
        run_compliance("COMP-6", vr, timestamp, {"NotADomain": "PASS"})
