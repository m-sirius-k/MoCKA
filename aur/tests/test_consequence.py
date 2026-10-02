"""
Tests for ConsequenceRecord creation and verification logic.
"""
import pytest
from datetime import datetime, timezone


class TestConsequenceRecord:
    def test_create_success_record(self):
        from aur.consequence import ConsequenceRecord, create_consequence
        r = create_consequence(
            action_id="test-action-001",
            assessment_id="ASSESS-20261002-abcd1234",
            execution_success=True,
            actual_changes=["structural/foo.py modified"],
            expected_changes=["structural/foo.py modified"],
            verification_method="git_diff",
        )
        assert isinstance(r, ConsequenceRecord)
        assert r.outcome == "SUCCESS"
        assert r.deviation == []
        assert r.consequence_id.startswith("CONSQ-")

    def test_create_failure_record(self):
        from aur.consequence import create_consequence
        r = create_consequence(
            action_id="test-action-002",
            assessment_id="ASSESS-20261002-abcd1234",
            execution_success=False,
            actual_changes=[],
            expected_changes=["structural/bar.py modified"],
            verification_method="git_diff",
            error_detail="FileNotFoundError: structural/bar.py",
        )
        assert r.outcome == "FAILURE"
        assert r.execution_success is False

    def test_partial_outcome_when_deviation_exists(self):
        from aur.consequence import create_consequence
        r = create_consequence(
            action_id="test-action-003",
            assessment_id="ASSESS-20261002-abcd1234",
            execution_success=True,
            actual_changes=["structural/baz.py modified", "structural/extra.py added"],
            expected_changes=["structural/baz.py modified"],
            verification_method="git_diff",
        )
        assert r.outcome == "PARTIAL"
        assert len(r.deviation) > 0

    def test_unknown_outcome_when_not_verified(self):
        from aur.consequence import create_consequence
        r = create_consequence(
            action_id="test-action-004",
            assessment_id="ASSESS-20261002-abcd1234",
            execution_success=True,
            actual_changes=[],
            expected_changes=["structural/qux.py modified"],
            verification_method="unverified",
        )
        assert r.outcome == "UNKNOWN"
        assert r.consequence_verified is False

    def test_consequence_has_required_fields(self):
        from aur.consequence import create_consequence
        r = create_consequence(
            action_id="test-action-005",
            assessment_id="ASSESS-20261002-abcd1234",
            execution_success=True,
            actual_changes=[],
            expected_changes=[],
            verification_method="git_diff",
        )
        assert hasattr(r, "consequence_id")
        assert hasattr(r, "action_id")
        assert hasattr(r, "assessment_id")
        assert hasattr(r, "timestamp")
        assert hasattr(r, "execution_success")
        assert hasattr(r, "consequence_verified")
        assert hasattr(r, "verification_method")
        assert hasattr(r, "actual_changes")
        assert hasattr(r, "expected_changes")
        assert hasattr(r, "deviation")
        assert hasattr(r, "outcome")
