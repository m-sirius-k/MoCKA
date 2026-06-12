# phios/meaning/interaction.py
"""Meaning Interaction Layer — 意味の相互作用"""
from __future__ import annotations

from phios.meaning.state_vector import MeaningStateVector


def interact(a: MeaningStateVector, b: MeaningStateVector) -> MeaningStateVector:
    """
    2つの意味ベクトルを相互作用させる。

    ルール:
      intent_weight:  平均（協調）
      impact_weight:  最大値（最悪ケース優先）
      urgency_weight: 最大値（緊急度は引き下げない）
      stability:      平均（安定度は平滑化）
      entropy:        差の絶対値（意味のズレが揺らぎになる）
    """
    result = MeaningStateVector(
        intent_weight=(a.intent_weight + b.intent_weight) / 2,
        impact_weight=max(a.impact_weight, b.impact_weight),
        urgency_weight=max(a.urgency_weight, b.urgency_weight),
        stability=(a.stability + b.stability) / 2,
        entropy=abs(a.entropy - b.entropy),
    )
    result.normalize()
    return result
