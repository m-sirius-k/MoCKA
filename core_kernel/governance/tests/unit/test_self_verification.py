"""Unit tests for self_verification.

Confirms the Design -> Contract -> Implementation -> Unit Test ->
Integration Test -> Evidence chain is detected as consistent, and
that a deliberately broken requirement is detected as missing.
"""

from __future__ import annotations

from pathlib import Path

from core_kernel.governance.self_verification import SelfVerificationEngine, VerificationStatus
from core_kernel.governance.self_verification.audit_report import generate_audit_report
from core_kernel.governance.self_verification.requirement_map import REQUIREMENTS


def test_all_requirements_have_no_missing_links():
    engine = SelfVerificationEngine()
    report = engine.run()
    for rr in report.requirement_results:
        assert rr.status is VerificationStatus.PASS, (rr.requirement.req_id, rr.missing_links)


def test_overall_report_is_pass_with_no_evidence_findings():
    engine = SelfVerificationEngine()
    report = engine.run()
    assert report.test_exit_code == 0
    assert report.evidence_findings == ()
    assert report.status is VerificationStatus.PASS


def test_audit_report_is_serializable_and_complete():
    engine = SelfVerificationEngine()
    report = engine.run()
    summary = generate_audit_report(report)
    assert summary["status"] == "PASS"
    assert {r["req_id"] for r in summary["requirements"]} == {r.req_id for r in REQUIREMENTS}
    assert set(summary["evidence_scenarios"]) == {"pass", "warning", "fail"}


def test_missing_implementation_file_is_detected(tmp_path):
    from core_kernel.governance.self_verification.verification_engine import _check_requirement_files
    from core_kernel.governance.self_verification.requirement_map import Requirement

    bogus = Requirement(
        req_id="REQ-BOGUS-001",
        title="Nonexistent module",
        design=Path("docs/governance/DOES_NOT_EXIST.md"),
        contract=Path("core_kernel/governance/contracts/validation_contract.py"),
        implementation=(Path("core_kernel/governance/engines/does_not_exist.py"),),
        unit_test=Path("core_kernel/governance/tests/unit/test_validation_engine.py"),
        integration_test=None,
    )
    missing = _check_requirement_files(bogus, Path(".").resolve())
    assert any("DOES_NOT_EXIST" in m for m in missing)
    assert any("does_not_exist.py" in m for m in missing)
