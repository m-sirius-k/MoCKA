# phios/core/semantic_router.py
"""SemanticRouter v1.1 — routing専念（実行しない）"""
from __future__ import annotations

from phios.core.decision_synthesis import Action
from phios.core.adapter_manager import list_adapters


class SemanticRouter:
    """
    Actionを見て「どこへ送るか」だけを決める。
    実行はExecutorが担当。
    """

    def route(self, action: Action) -> dict:
        """
        戻り値:
          destination: "human_gate" | "verify_all" | adapter_id | "mock_fallback" | "ledger"
          routable:    bool
        """
        if action.action_type == "noop":
            return {"destination": "ledger", "routable": False}

        if action.target == "human_gate":
            return {
                "destination": "human_gate",
                "routable": False,
                "requires_human": True,
                "gate_reason": action.reason,
                "gate_origin_event": action.action_type,
            }

        if action.target == "verify_all":
            return {"destination": "verify_all", "routable": True}

        adapters = list_adapters()
        if action.target in adapters:
            return {"destination": action.target, "routable": True}

        return {"destination": "mock_fallback", "routable": True}
