# runtime/monitoring/observer.py
# MoCKA v1.2.1+ — Observer（観測統合）
# 責務: 全state出力をObserverを通して統一形式に変換する。
# 設計原則: ALL STATE OUTPUTS MUST PASS THROUGH OBSERVER

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class Observer:
    """
    run_cycle の結果を受け取り、統一出力形式に変換する。
    データを変更しない。形式を統一するだけ。
    """

    def snapshot(self, cycle_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        統一出力形式に変換する。

        Returns:
            {
                "cycle":     "001",
                "decision":  "TAG",
                "drift":     "high",
                "stability": "HIGH",
                "audit":     "STABLE",
                "health":    "OK",
                "timestamp": "..."
            }
        """
        state = result.get("state", {})
        audit = result.get("audit", {})

        return {
            "cycle":     cycle_id,
            "decision":  result.get("decision", "UNKNOWN"),
            "drift":     state.get("drift", "UNKNOWN"),
            "stability": state.get("stability", "UNKNOWN"),
            "audit":     audit.get("status", "UNKNOWN"),
            "health":    self._health(state, audit),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _health(self, state: Dict[str, Any], audit: Dict[str, Any]) -> str:
        """
        状態・監査結果からシステム健全性を判定する。
        PHI-OSや意味データは変更しない。観測のみ。
        """
        if audit.get("consistency") == "INTEGRITY_FAIL":
            return "CRITICAL"
        if state.get("stability") == "LOW":
            return "DEGRADED"
        if state.get("stability") == "MEDIUM":
            return "CAUTION"
        return "OK"
