# audit/system_audit.py
# MoCKA v1.2.1 — System Audit Layer
# 責務: CognitiveCore の出力を検証し、整合性・安定性レポートを生成する。
# 設計原則: データ変更なし。観測・判定のみ。

from __future__ import annotations

from typing import Any, Dict

from core.timeline.semantic_timeline_engine import SemanticTimelineEngine
from audit.consistency_check import check_system_integrity
from audit.drift_report import generate_report


class SystemAudit:

    def __init__(self, timeline: SemanticTimelineEngine) -> None:
        self.timeline = timeline

    def check(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "consistency": self._consistency(state),
            "drift":       self._drift(state),
            "status":      self._status(state),
            "compliance":  self._compliance(),
        }

    def _consistency(self, state: Dict[str, Any]) -> str:
        ok = check_system_integrity()
        return "OK" if ok else "INTEGRITY_FAIL"

    def _drift(self, state: Dict[str, Any]) -> str:
        return state.get("drift", "UNKNOWN")

    def _status(self, state: Dict[str, Any]) -> str:
        if state.get("stability") == "HIGH":
            return "STABLE"
        if state.get("stability") == "LOW":
            return "ALERT"
        return "MONITOR"

    def _compliance(self) -> str:
        """制度適合性: append-only / 非改変 / 記録義務の確認。"""
        report = generate_report()
        if report.get("risk") == "HIGH":
            return "REVIEW_REQUIRED"
        return "VALID"
