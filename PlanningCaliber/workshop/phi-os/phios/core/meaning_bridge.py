# phios/core/meaning_bridge.py
"""Meaning Bridge — Phase 3（離散意味）→ Phase 4（連続意味）接続"""
from __future__ import annotations

from phios.core.event_interpreter import InterpretedEvent
from phios.meaning.state_vector import MeaningStateVector


def to_vector(event: InterpretedEvent) -> MeaningStateVector:
    """
    InterpretedEvent（Phase 3の離散意味）を
    MeaningStateVector（Phase 4の連続意味）に変換する。
    """
    urgency_normalized = event.meaning["urgency"] / 3.0  # 1〜3 -> 0.33〜1.0

    impact_map = {
        "critical": 1.0,
        "system": 0.5,
        "local": 0.2,
    }
    impact_weight = impact_map.get(event.meaning["impact"], 0.2)

    return MeaningStateVector(
        intent_weight=urgency_normalized,
        impact_weight=impact_weight,
        urgency_weight=urgency_normalized,
        stability=0.5,
        entropy=0.1,
    )


def from_vector(vector: MeaningStateVector) -> dict:
    """
    MeaningStateVectorを Phase 3互換の意味辞書に逆変換する（参照用）。
    """
    return {
        "intent": "transition" if vector.intent_weight > 0.6 else "observe",
        "impact": "critical" if vector.is_critical() else "system" if vector.impact_weight > 0.4 else "local",
        "urgency": round(vector.urgency_weight * 3),
    }
