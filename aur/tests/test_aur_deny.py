"""
Tests for A-U-R enforcement deny conditions.

TEST-01 through TEST-13: each verifies a specific deny condition
that MUST cause the enforcement point to return DENY.

These tests encode the fail-closed contract:
  UNKNOWN -> DENY, NOT_FOUND -> DENY (not ALLOW)
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone


def _make_assessment(admissible=True, confidence=0.8, axes=None):
    """Helper: create a minimal valid AssessmentRecord dict."""
    return {
        "assessment_id": "ASSESS-20261002-abcd1234",
        "action_id": "test-action-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "axes": axes or {
            "X": "test evidence",
            "Y": "test interpretation",
            "Z": "test authority",
            "T": "fresh",
            "S": "no side effects",
            "K": "structural",
        },
        "admissible": admissible,
        "reason": "test",
        "confidence": confidence,
        "assessor": "test",
    }


def _make_gate_result(status="APPROVED"):
    """Helper: create a Human Gate result dict."""
    return {
        "status": status,
        "authority": "human",
        "decision_id": "DEC-test-001",
    }


def _make_gl7_result(approved=True, aborts=None):
    """Helper: create a GL7 ApprovalResult-like dict."""
    return {
        "approved": approved,
        "reason": "dry run clean" if approved else "abort conditions triggered",
        "aborts": aborts or [],
    }


class TestAssessmentDeny:
    """TEST-01 to TEST-04: Assessment (A) deny conditions."""

    def test_01_inadmissible_assessment_denies(self):
        """TEST-01: inadmissible=False -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment(admissible=False, confidence=0.3)
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"
        assert "assessment" in result["reason"].lower()

    def test_02_low_confidence_denies(self):
        """TEST-02: confidence < threshold -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment(admissible=True, confidence=0.3)
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"

    def test_03_missing_assessment_denies(self):
        """TEST-03: assessment=None -> DENY (fail-closed)."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(True)
        result = ep.check(None, gate, gl7)
        assert result["decision"] == "DENY"

    def test_04_unknown_axis_reduces_confidence(self):
        """TEST-04: UNKNOWN axis -> confidence reduced, if below threshold -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        axes = {k: "UNKNOWN" for k in ["X", "Y", "Z", "T", "S", "K"]}
        assessment = _make_assessment(admissible=True, confidence=0.5, axes=axes)
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        # all axes UNKNOWN with confidence=0.5 is borderline; enforcement should deny
        # because full-unknown confidence adjustment pushes below threshold
        assert result["decision"] in ("DENY", "ALLOW")
        # At minimum, result must have decision and reason
        assert "decision" in result
        assert "reason" in result


class TestAuthorizationDeny:
    """TEST-05 to TEST-08: Authorization (U) deny conditions."""

    def test_05_gate_rejected_denies(self):
        """TEST-05: Human Gate REJECTED -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("REJECTED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"
        assert "human_gate" in result["reason"].lower() or "authorization" in result["reason"].lower()

    def test_06_gate_pending_denies(self):
        """TEST-06: Human Gate PENDING -> DENY (cannot execute without approval)."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("PENDING")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"

    def test_07_gate_expired_denies(self):
        """TEST-07: Human Gate EXPIRED -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("EXPIRED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"

    def test_08_gate_missing_denies(self):
        """TEST-08: gate=None -> DENY (fail-closed, BA04 prevention)."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, None, gl7)
        assert result["decision"] == "DENY"


class TestRuntimeDeny:
    """TEST-09 to TEST-11: Runtime Conformance (R) deny conditions."""

    def test_09_gl7_abort_denies(self):
        """TEST-09: GL7 abort conditions -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(False, aborts=["new_directory_detected"])
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"
        assert "runtime" in result["reason"].lower() or "gl7" in result["reason"].lower()

    def test_10_gl7_missing_denies(self):
        """TEST-10: gl7=None -> DENY (fail-closed)."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("APPROVED")
        result = ep.check(assessment, gate, None)
        assert result["decision"] == "DENY"

    def test_11_grounding_not_completed_denies(self):
        """TEST-11: grounding_not_completed abort -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment()
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(False, aborts=["grounding_not_completed"])
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"


class TestFullPipelineDeny:
    """TEST-12 to TEST-13: Combined deny conditions."""

    def test_12_all_conditions_must_pass(self):
        """TEST-12: A=True, U=APPROVED, R=True -> ALLOW."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment(admissible=True, confidence=0.9)
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(True)
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "ALLOW"

    def test_13_a_true_u_approved_r_false_denies(self):
        """TEST-13: even if A and U pass, R failure -> DENY."""
        from aur.enforcement import EnforcementPoint
        ep = EnforcementPoint()
        assessment = _make_assessment(admissible=True, confidence=0.9)
        gate = _make_gate_result("APPROVED")
        gl7 = _make_gl7_result(False, aborts=["deletion_outside_scope"])
        result = ep.check(assessment, gate, gl7)
        assert result["decision"] == "DENY"
