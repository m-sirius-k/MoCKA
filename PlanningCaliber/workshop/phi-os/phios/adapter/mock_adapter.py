# phi_os/adapter/mock_adapter.py
"""MockAdapter — safe_boot() の最低保証として常に登録されるテスト用Adapter"""
from __future__ import annotations
from datetime import datetime, timezone

from adapter.adapter_interface import AIAdapter


class MockAdapter(AIAdapter):
    AI_ID = "mock"

    def handshake(self, scope: str = "institution_state") -> dict:
        return {
            "status": "ok",
            "ai_id": self.AI_ID,
            "trust_level": "trial",
            "capabilities": ["CAP_STATE_READ"],
            "scope": scope,
        }

    def receive_commission(self, commission: dict) -> bool:
        return bool(commission.get("commission_id"))

    def execute(self, commission: dict) -> dict:
        return {"result": f"[mock] executed: {commission.get('task', '')}"}

    def ack(self, result: dict) -> dict:
        return {
            "ok": True,
            "actor": self.AI_ID,
            "result": result,
            "responded_at": datetime.now(timezone.utc).isoformat(),
        }
