"""Phase 8: SLA record definition."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SLARecord:
    service_name: str
    availability: float          # 0-100 (%)
    latency_ms: float             # lower is better
    error_rate: float             # 0-1 (fraction)
    integrity_score: float        # 0-100
    reproducibility_score: float  # 0-100


# SLA scoring constants
SLA_PASS_THRESHOLD = 85.0

LATENCY_TARGET_MS = 200.0   # latency at/under this scores full marks
LATENCY_MAX_MS = 2000.0     # latency at/over this scores zero

ERROR_RATE_MAX = 0.05       # error rate at/over this scores zero
