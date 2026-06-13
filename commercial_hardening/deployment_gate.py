# -*- coding: utf-8 -*-
"""Deployment Gate (Phase 6 Commercial Hardening Layer) - 商用ゲート

必須条件 (全て満たさなければPASS不可):
  - all integration tests PASS
  - stress test PASS
  - consistency score >= 0.85
  - failure containment verified (全zone healthy)
"""

from dataclasses import dataclass, field

CONSISTENCY_SCORE_THRESHOLD = 0.85


@dataclass
class GateResult:
    passed: bool
    reasons: list = field(default_factory=list)


def check(integration_tests_passed: bool, stress_tests_passed: bool,
          consistency_score: float, containment_verified: bool) -> GateResult:
    reasons = []

    if not integration_tests_passed:
        reasons.append("integration tests failed")
    if not stress_tests_passed:
        reasons.append("stress tests failed")
    if consistency_score < CONSISTENCY_SCORE_THRESHOLD:
        reasons.append(f"consistency score {consistency_score} < {CONSISTENCY_SCORE_THRESHOLD}")
    if not containment_verified:
        reasons.append("failure containment not verified")

    return GateResult(passed=not reasons, reasons=reasons)
