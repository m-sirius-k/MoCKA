"""Phase 8: Production Readiness Scoring (PRS)."""

from __future__ import annotations

from enum import Enum


class ReadinessLevel(str, Enum):
    PRODUCTION_ELIGIBLE = "production_eligible"
    LIMITED_RELEASE = "limited_release"
    BLOCKED = "blocked"


PRODUCTION_ELIGIBLE_THRESHOLD = 95.0
LIMITED_RELEASE_THRESHOLD = 80.0

# incident_count >= this many incidents drives the incident component to zero
INCIDENT_ZERO_THRESHOLD = 5


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _to_score(value) -> float:
    """Normalize a metric to a 0-100 score. Accepts bool, fraction (0-1), or 0-100."""
    if isinstance(value, bool):
        return 100.0 if value else 0.0
    value = float(value)
    if 0.0 <= value <= 1.0:
        return value * 100.0
    return _clamp(value)


def _incident_score(incident_count: int) -> float:
    if incident_count <= 0:
        return 100.0
    if incident_count >= INCIDENT_ZERO_THRESHOLD:
        return 0.0
    return _clamp(100.0 * (INCIDENT_ZERO_THRESHOLD - incident_count) / INCIDENT_ZERO_THRESHOLD)


class PRSEngine:
    """Weighted Production Readiness Score.

    Components:
    - test_coverage: 25%
    - incident_count (fewer is better): 20%
    - telemetry_completeness: 20%
    - rollback_support: 15%
    - contract_compliance: 20%
    """

    WEIGHTS = {
        "test_coverage": 0.25,
        "incident_count": 0.20,
        "telemetry_completeness": 0.20,
        "rollback_support": 0.15,
        "contract_compliance": 0.20,
    }

    REQUIRED_KEYS = (
        "test_coverage",
        "incident_count",
        "telemetry_completeness",
        "rollback_support",
        "contract_compliance",
    )

    def score(self, metrics: dict) -> float:
        missing = [key for key in self.REQUIRED_KEYS if key not in metrics]
        if missing:
            raise ValueError(f"PRS metrics missing required keys: {missing}")

        component_scores = {
            "test_coverage": _to_score(metrics["test_coverage"]),
            "incident_count": _incident_score(int(metrics["incident_count"])),
            "telemetry_completeness": _to_score(metrics["telemetry_completeness"]),
            "rollback_support": _to_score(metrics["rollback_support"]),
            "contract_compliance": _to_score(metrics["contract_compliance"]),
        }

        total = sum(component_scores[key] * weight for key, weight in self.WEIGHTS.items())
        return round(total, 4)

    def level(self, prs_score: float) -> ReadinessLevel:
        if prs_score >= PRODUCTION_ELIGIBLE_THRESHOLD:
            return ReadinessLevel.PRODUCTION_ELIGIBLE
        if prs_score >= LIMITED_RELEASE_THRESHOLD:
            return ReadinessLevel.LIMITED_RELEASE
        return ReadinessLevel.BLOCKED
