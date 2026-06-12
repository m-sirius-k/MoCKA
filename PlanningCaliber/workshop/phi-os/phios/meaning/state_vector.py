# phios/meaning/state_vector.py
"""Meaning State Vector — 意味の状態表現"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MeaningStateVector:
    intent_weight: float   # 0.0 - 1.0
    impact_weight: float   # 0.0 - 1.0
    urgency_weight: float  # 0.0 - 1.0
    stability: float        # 意味の固定度（0.0=不安定 / 1.0=完全固定）
    entropy: float           # 意味の揺らぎ（0.0=確定 / 1.0=最大不確実）

    def normalize(self) -> None:
        """intent/impact/urgencyの合計を1.0に正規化する"""
        total = self.intent_weight + self.impact_weight + self.urgency_weight
        if total == 0:
            return
        self.intent_weight /= total
        self.impact_weight /= total
        self.urgency_weight /= total

    def is_stable(self, threshold: float = 0.7) -> bool:
        return self.stability >= threshold

    def is_critical(self, threshold: float = 0.8) -> bool:
        return self.impact_weight >= threshold
