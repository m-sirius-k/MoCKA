# -*- coding: utf-8 -*-
"""Degradation Controller (Phase 6 Commercial Hardening Layer)

制御:
  - performance degrade detection : 直近の失敗率からdegradationを検知する
  - auto-simplification of pipeline : degraded時にoptionalステップをスキップする
  - load shedding                 : 過負荷時に低優先タスクを拒否する
"""

from dataclasses import dataclass, field

from commercial_hardening import production_mode_manager


@dataclass
class DegradationState:
    failure_count: int = 0
    total_count: int = 0
    degraded: bool = False

    @property
    def failure_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.failure_count / self.total_count


# degradation判定の閾値 (failure_rate >= この値でdegraded=True)
DEGRADE_THRESHOLD = 0.3
# degraded状態でskipするoptionalステップ名
OPTIONAL_STEPS = {"deep_analysis", "extended_audit", "telemetry_enrichment"}


class DegradationController:
    def __init__(self, mode_manager: production_mode_manager.ProductionModeManager = None):
        self.state = DegradationState()
        self.mode_manager = mode_manager or production_mode_manager.ProductionModeManager()

    def record(self, success: bool):
        self.state.total_count += 1
        if not success:
            self.state.failure_count += 1
        self.state.degraded = self.state.failure_rate >= DEGRADE_THRESHOLD

    def simplify_pipeline(self, steps: list) -> list:
        """degraded時はOPTIONAL_STEPSを除外したステップ列を返す。"""
        if not self.state.degraded:
            return list(steps)
        return [s for s in steps if s not in OPTIONAL_STEPS]

    def should_shed(self, priority: str) -> bool:
        """load shedding: degraded時、優先度"low"のタスクを拒否する。"""
        if not self.state.degraded:
            return False
        return priority == "low"

    def reset(self):
        self.state = DegradationState()
