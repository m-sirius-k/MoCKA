"""Phase 8: weighted SLA scoring."""

from __future__ import annotations

from sla.sla_definition import (
    ERROR_RATE_MAX,
    LATENCY_MAX_MS,
    LATENCY_TARGET_MS,
    SLA_PASS_THRESHOLD,
    SLARecord,
)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _latency_score(latency_ms: float) -> float:
    if latency_ms <= LATENCY_TARGET_MS:
        return 100.0
    if latency_ms >= LATENCY_MAX_MS:
        return 0.0
    span = LATENCY_MAX_MS - LATENCY_TARGET_MS
    return _clamp(100.0 * (LATENCY_MAX_MS - latency_ms) / span)


def _error_rate_score(error_rate: float) -> float:
    if error_rate <= 0:
        return 100.0
    if error_rate >= ERROR_RATE_MAX:
        return 0.0
    return _clamp(100.0 * (ERROR_RATE_MAX - error_rate) / ERROR_RATE_MAX)


class SLAEvaluator:
    """Weighted SLA scoring:
    - availability: 30%
    - latency: 20%
    - error_rate: 20%
    - integrity: 15%
    - reproducibility: 15%
    """

    WEIGHTS = {
        "availability": 0.30,
        "latency": 0.20,
        "error_rate": 0.20,
        "integrity": 0.15,
        "reproducibility": 0.15,
    }

    def evaluate(self, sla: SLARecord) -> float:
        component_scores = {
            "availability": _clamp(sla.availability),
            "latency": _latency_score(sla.latency_ms),
            "error_rate": _error_rate_score(sla.error_rate),
            "integrity": _clamp(sla.integrity_score),
            "reproducibility": _clamp(sla.reproducibility_score),
        }

        score = sum(component_scores[key] * weight for key, weight in self.WEIGHTS.items())
        return round(score, 4)

    def passes(self, sla: SLARecord) -> bool:
        return self.evaluate(sla) >= SLA_PASS_THRESHOLD
