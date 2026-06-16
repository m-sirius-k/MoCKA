# core/phi/phi_bridge_governance.py
# MoCKA v1.2.1 — PHI-OS (純粋classify層)
# 責務: ConflictRecord を受け取り OBSERVE / TAG / ROUTE を返すだけ。
# 設計原則: 意味を変更しない。判断しない。分類するだけ。副作用なし。

from __future__ import annotations

from core.bridge.phi_personal_bridge import ConflictRecord


class PhiOS:
    """
    PHI-OS は純粋な分類器。
    severity のみを見て決定する。外部状態を変更しない。
    """

    def classify(self, conflict: ConflictRecord) -> str:
        """
        severity に基づく3分岐分類。

        Returns:
            "OBSERVE" — 通常監視
            "TAG"     — 要注目
            "ROUTE"   — 経路変更推奨
        """
        if conflict.severity < 0.3:
            return "OBSERVE"
        if conflict.severity < 0.7:
            return "TAG"
        return "ROUTE"
