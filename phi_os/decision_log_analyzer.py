# phi_os/decision_log_analyzer.py
# MoCKA v1.1 — PHI-OS Decision Log Analyzer
# 責務: PHI-OSの判断を「評価対象」に変える層
# 設計原則: PHI-OSは変更しない。その振る舞いを外部から分析するだけ。

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

# SemanticTimelineEngine からイベントを読む（依存注入でも可）
from timeline.semantic_timeline_engine import SemanticTimelineEngine, SemanticEvent


# ─────────────────────────────────────────────────────────────
# 既知の PHI-OS ルーティングラベル
# ─────────────────────────────────────────────────────────────

KNOWN_DECISIONS = {"OBSERVE", "TAG", "ROUTE", "BLOCK"}


# ─────────────────────────────────────────────────────────────
# DecisionLogAnalyzer
# ─────────────────────────────────────────────────────────────

class DecisionLogAnalyzer:
    """
    PHI-OSの意思決定ログをSemanticTimelineEngineから読み込み、
    バイアス・ルーティングパターン・安定性を分析する。
    PHI-OS本体には一切触れない。
    """

    def __init__(self, timeline: Optional[SemanticTimelineEngine] = None) -> None:
        self._timeline = timeline or SemanticTimelineEngine()

    def _events(self, term: Optional[str] = None) -> List[SemanticEvent]:
        if term:
            return self._timeline.get_timeline(term)
        return self._timeline._load_all()

    # ── ① analyze_bias ───────────────────────────────────────

    def analyze_bias(self, term: Optional[str] = None) -> Dict[str, Any]:
        """
        PHI decision と Personal value の偏り検出。
        PHI/Personal の値が一致する割合 vs 乖離する割合を集計する。
        """
        events = self._events(term)
        if not events:
            return {"term": term, "total": 0, "bias": "NO_DATA"}

        phi_dominated = sum(
            1 for e in events
            if e.conflict_state in ("DRIFT", "CONFLICT")
            and e.phi_decision in ("ROUTE", "BLOCK")
        )
        aligned = sum(1 for e in events if e.conflict_state == "NORMAL")
        total = len(events)

        phi_rate = round(phi_dominated / total, 4)

        if phi_rate >= 0.5:
            bias_label = "PHI偏重"
        elif aligned / total >= 0.7:
            bias_label = "BALANCED"
        else:
            bias_label = "PERSONAL偏重"

        return {
            "term":           term,
            "total":          total,
            "phi_dominated":  phi_dominated,
            "aligned":        aligned,
            "phi_rate":       phi_rate,
            "bias":           bias_label,
        }

    # ── ② detect_routing_pattern ─────────────────────────────

    def detect_routing_pattern(self, term: Optional[str] = None) -> Dict[str, Any]:
        """
        OBSERVE / TAG / ROUTE / BLOCK の比率分析。
        PHI-OSの傾向を検出する。
        """
        events = self._events(term)
        if not events:
            return {"term": term, "total": 0, "pattern": {}, "dominant": "NO_DATA"}

        counter: Counter = Counter(e.phi_decision for e in events)
        total = len(events)

        pattern = {
            label: {
                "count": counter.get(label, 0),
                "rate":  round(counter.get(label, 0) / total, 4),
            }
            for label in KNOWN_DECISIONS
        }

        dominant = counter.most_common(1)[0][0] if counter else "UNKNOWN"

        return {
            "term":     term,
            "total":    total,
            "pattern":  pattern,
            "dominant": dominant,
        }

    # ── ③ stability_score ────────────────────────────────────

    def stability_score(self, term: Optional[str] = None, window: int = 20) -> Dict[str, Any]:
        """
        system stability = conflict処理の一貫性。
        直近 window 件で phi_decision が支配的なラベルと一致する割合。
        """
        events = self._events(term)
        recent = events[-window:] if len(events) > window else events

        if not recent:
            return {"term": term, "stability": 0.0, "level": "NO_DATA"}

        counter: Counter = Counter(e.phi_decision for e in recent)
        dominant_count = counter.most_common(1)[0][1] if counter else 0
        score = round(dominant_count / len(recent), 4)

        if score >= 0.7:
            level = "HIGH"
        elif score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "term":      term,
            "window":    len(recent),
            "stability": score,
            "level":     level,
        }

    # ── 統合レポート ──────────────────────────────────────────

    def report(self, term: str) -> str:
        """指定タームの分析結果を可読テキストで返す。"""
        bias    = self.analyze_bias(term)
        routing = self.detect_routing_pattern(term)
        stab    = self.stability_score(term)

        route_rate   = routing["pattern"].get("ROUTE",   {}).get("rate", 0.0)
        observe_rate = routing["pattern"].get("OBSERVE", {}).get("rate", 0.0)

        lines = [
            f'TERM: "{term}"',
            f'ROUTE RATE:   {route_rate:.2f}',
            f'OBSERVE RATE: {observe_rate:.2f}',
            f'BIAS:         {bias["bias"]}',
            f'STABILITY:    {stab["level"]}',
            f'TOTAL EVENTS: {bias["total"]}',
        ]
        return "\n".join(lines)

    def report_all(self) -> List[str]:
        """全タームのレポートを一括生成する。"""
        summary = self._timeline.summary()
        return [self.report(term) for term in summary.get("terms", {})]
