"""
Tests for Reassessment module (Experience Memory -> Assessment context bridge).
"""
import pytest


class TestReassessment:
    def test_no_prior_data_returns_neutral_context(self):
        from aur.reassessment import Reassessment
        r = Reassessment()
        ctx = r.build_context(action_id="never-seen-action", axes={})
        assert ctx.has_prior_data is False
        assert ctx.confidence_adjustment == 0.0
        assert ctx.warnings == []

    def test_failure_pattern_reduces_confidence(self):
        from aur.reassessment import Reassessment, ReassessmentContext
        r = Reassessment()
        # Inject a mock failure experience
        r._inject_test_experience({
            "action_id": "test-repeated-action",
            "outcome": "FAILURE",
            "lesson": "scope exceeded expected files",
            "lesson_type": "FAILURE_PATTERN",
            "axes_snapshot": {"X": "test"},
        })
        ctx = r.build_context(action_id="test-repeated-action", axes={})
        assert ctx.has_prior_data is True
        assert ctx.confidence_adjustment < 0.0
        assert len(ctx.failure_patterns) > 0

    def test_success_pattern_increases_confidence(self):
        from aur.reassessment import Reassessment
        r = Reassessment()
        r._inject_test_experience({
            "action_id": "test-success-action",
            "outcome": "SUCCESS",
            "lesson": "clean execution within scope",
            "lesson_type": "SUCCESS_PATTERN",
            "axes_snapshot": {"X": "test"},
        })
        ctx = r.build_context(action_id="test-success-action", axes={})
        assert ctx.has_prior_data is True
        assert ctx.confidence_adjustment >= 0.0

    def test_reassessment_context_has_required_fields(self):
        from aur.reassessment import Reassessment
        r = Reassessment()
        ctx = r.build_context(action_id="field-check-action", axes={})
        assert hasattr(ctx, "reassessment_id")
        assert hasattr(ctx, "action_id")
        assert hasattr(ctx, "timestamp")
        assert hasattr(ctx, "prior_outcomes")
        assert hasattr(ctx, "failure_patterns")
        assert hasattr(ctx, "success_patterns")
        assert hasattr(ctx, "confidence_adjustment")
        assert hasattr(ctx, "warnings")
        assert hasattr(ctx, "similar_experience_count")
        assert hasattr(ctx, "has_prior_data")

    def test_confidence_adjustment_clamped(self):
        from aur.reassessment import Reassessment
        r = Reassessment()
        for i in range(10):
            r._inject_test_experience({
                "action_id": "over-fail-action",
                "outcome": "FAILURE",
                "lesson": f"failure {i}",
                "lesson_type": "FAILURE_PATTERN",
                "axes_snapshot": {},
            })
        ctx = r.build_context(action_id="over-fail-action", axes={})
        assert ctx.confidence_adjustment >= -0.5
        assert ctx.confidence_adjustment <= 0.5
