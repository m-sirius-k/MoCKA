# phios/meaning/conflict.py
"""Meaning Conflict Resolver — 意味の衝突解決"""
from __future__ import annotations

from phios.meaning.state_vector import MeaningStateVector
from phios.meaning.interaction import interact


def resolve_conflict(a: MeaningStateVector, b: MeaningStateVector) -> MeaningStateVector:
    """
    2つの意味ベクトルが衝突したとき、解決ルールを適用する。

    優先順位:
      1. critical優先（impact > 0.8 の方を採用）
      2. 安定度優先（stability差が0.5以上の場合、安定な方を採用）
      3. デフォルト融合（interact()で平滑化）
    """
    if max(a.impact_weight, b.impact_weight) > 0.8:
        return a if a.impact_weight > b.impact_weight else b

    if abs(a.stability - b.stability) > 0.5:
        return a if a.stability > b.stability else b

    return interact(a, b)


def detect_conflict(a: MeaningStateVector, b: MeaningStateVector) -> bool:
    """2つのベクトルが意味衝突しているか判定する"""
    intent_diff = abs(a.intent_weight - b.intent_weight)
    impact_diff = abs(a.impact_weight - b.impact_weight)
    entropy_diff = abs(a.entropy - b.entropy)
    return intent_diff > 0.5 or impact_diff > 0.5 or entropy_diff > 0.5
