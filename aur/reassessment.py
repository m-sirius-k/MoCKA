"""
aur/reassessment.py: Reassessment — Experience Memory -> Assessment context bridge.

Contract: docs/contracts/reassessment_contract_v1.md
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ReassessmentContext:
    reassessment_id: str
    action_id: str
    timestamp: str
    prior_outcomes: list
    failure_patterns: list
    success_patterns: list
    confidence_adjustment: float
    warnings: list
    similar_experience_count: int
    has_prior_data: bool


class Reassessment:
    """
    Queries experience memory for an action and builds a ReassessmentContext
    that can be passed to create_assessment() to adjust confidence.
    """

    FAILURE_PENALTY = -0.1
    SUCCESS_BONUS = 0.05
    DEVIATION_PENALTY = -0.05
    MAX_FAILURE_PENALTY = -0.4
    MAX_SUCCESS_BONUS = 0.2
    ADJUSTMENT_CLAMP = 0.5

    def __init__(self):
        self._test_experiences: list[dict] = []

    def _inject_test_experience(self, exp: dict) -> None:
        """Test hook: inject a mock experience for unit tests."""
        self._test_experiences.append(exp)

    def _load_experiences(self, action_id: str) -> list[dict]:
        """
        Load experience memory entries for the given action_id.
        Falls back to test_experiences if memory store is unavailable.
        """
        entries = []
        try:
            from memory.experience_memory import load_experience_entries
            all_entries = load_experience_entries()
            for e in all_entries:
                content = e.get("content", {})
                if content.get("action_id") == action_id:
                    entries.append(content)
        except Exception:
            pass

        for e in self._test_experiences:
            if e.get("action_id") == action_id:
                entries.append(e)

        return entries

    def build_context(self, action_id: str, axes: dict) -> ReassessmentContext:
        """
        Build a ReassessmentContext from experience memory for the given action.
        Returns a neutral context (has_prior_data=False) if no experiences found.
        """
        reassessment_id = (
            f"REASSESS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        )
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            experiences = self._load_experiences(action_id)
        except Exception:
            experiences = []

        if not experiences:
            return ReassessmentContext(
                reassessment_id=reassessment_id,
                action_id=action_id,
                timestamp=timestamp,
                prior_outcomes=[],
                failure_patterns=[],
                success_patterns=[],
                confidence_adjustment=0.0,
                warnings=[],
                similar_experience_count=0,
                has_prior_data=False,
            )

        prior_outcomes = [e.get("outcome", "UNKNOWN") for e in experiences]
        failure_patterns = [
            e.get("lesson", "") for e in experiences
            if e.get("lesson_type") == "FAILURE_PATTERN"
        ]
        success_patterns = [
            e.get("lesson", "") for e in experiences
            if e.get("lesson_type") == "SUCCESS_PATTERN"
        ]
        deviation_patterns = [
            e.get("lesson", "") for e in experiences
            if e.get("lesson_type") == "DEVIATION_PATTERN"
        ]

        failure_count = prior_outcomes.count("FAILURE")
        success_count = prior_outcomes.count("SUCCESS")
        deviation_count = len(deviation_patterns)

        raw_adjustment = (
            max(self.FAILURE_PENALTY * failure_count, self.MAX_FAILURE_PENALTY)
            + min(self.SUCCESS_BONUS * success_count, self.MAX_SUCCESS_BONUS)
            + self.DEVIATION_PENALTY * deviation_count
        )
        adjustment = max(-self.ADJUSTMENT_CLAMP, min(self.ADJUSTMENT_CLAMP, raw_adjustment))

        warnings = []
        for fp in failure_patterns[:3]:
            if fp:
                warnings.append(f"Past failure: {fp[:100]}")
        for dp in deviation_patterns[:2]:
            if dp:
                warnings.append(f"Past deviation: {dp[:100]}")

        return ReassessmentContext(
            reassessment_id=reassessment_id,
            action_id=action_id,
            timestamp=timestamp,
            prior_outcomes=prior_outcomes,
            failure_patterns=failure_patterns,
            success_patterns=success_patterns,
            confidence_adjustment=adjustment,
            warnings=warnings,
            similar_experience_count=len(experiences),
            has_prior_data=True,
        )
