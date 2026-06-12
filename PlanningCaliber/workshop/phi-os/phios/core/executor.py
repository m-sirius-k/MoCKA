# phios/core/executor.py
"""Executor — routingされたActionを実行する"""
from __future__ import annotations

from phios.core.adapter_manager import get
from phios.core.execution_gate import gate_check


class Executor:
    """
    SemanticRouterが決めた destination に従って実行する。
    実行の詳細を全てここに集約する。
    """

    def execute(self, route_result: dict, action) -> dict:
        dest = route_result.get("destination")

        if not route_result.get("routable"):
            return {
                "executed": False,
                "destination": dest,
                "reason": route_result.get("gate_reason", "noop"),
            }

        if dest == "verify_all":
            ok = gate_check()
            return {"executed": True, "destination": dest, "ok": ok}

        adapter_id = "mock" if dest == "mock_fallback" else dest
        try:
            adapter = get(adapter_id)
            result = adapter.execute({"task": action.reason, "priority": action.priority})
            ack = adapter.ack(result)
            return {"executed": True, "destination": adapter_id, "result": result, "ack": ack}
        except Exception as e:
            return {"executed": False, "destination": adapter_id, "error": str(e)}
