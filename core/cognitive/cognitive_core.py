# core/cognitive/cognitive_core.py
# MoCKA v1.2.1 — CognitiveCore (統合版)
# 責務: Timelineを観測し、system状態サマリを生成する。
# 設計原則: データ変更なし。読んで計算するだけ。

from __future__ import annotations

from typing import Any, Dict

from core.timeline.semantic_timeline_engine import SemanticTimelineEngine


class CognitiveCore:
    """
    Timeline を読み、bias / drift / stability を計算して返す。
    Analyzer / Signal / Loop を統合した単一観測層。
    """

    def __init__(self, timeline: SemanticTimelineEngine) -> None:
        self.timeline = timeline

    def summarize(self) -> Dict[str, Any]:
        """
        現在のシステム状態サマリを返す。
        データは変更しない。
        """
        events = self.timeline.load_all()

        if not events:
            return {"bias": "neutral", "drift": "low", "stability": "HIGH"}

        total = len(events)
        conflict_count = sum(1 for e in events if e.conflict_state != "NORMAL")
        drift_rate = conflict_count / total if total else 0.0

        # routing分布
        from collections import Counter
        decisions = Counter(e.phi_decision for e in events)
        route_rate = decisions.get("ROUTE", 0) / total if total else 0.0

        # bias判定
        if route_rate >= 0.5:
            bias = "PHI偏重"
        elif route_rate <= 0.2 and decisions.get("OBSERVE", 0) / total >= 0.5:
            bias = "PERSONAL偏重"
        else:
            bias = "neutral"

        # drift判定
        if drift_rate >= 0.6:
            drift = "high"
        elif drift_rate >= 0.3:
            drift = "medium"
        else:
            drift = "low"

        # stability判定
        recent = events[-20:]
        recent_conflict = sum(1 for e in recent if e.conflict_state != "NORMAL")
        recent_rate = recent_conflict / len(recent) if recent else 0.0

        if recent_rate < 0.3:
            stability = "HIGH"
        elif recent_rate < 0.6:
            stability = "MEDIUM"
        else:
            stability = "LOW"

        return {
            "bias":       bias,
            "drift":      drift,
            "stability":  stability,
            "total":      total,
            "drift_rate": round(drift_rate, 4),
            "route_rate": round(route_rate, 4),
        }
