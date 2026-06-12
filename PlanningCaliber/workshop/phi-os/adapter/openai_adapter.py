"""OpenAI Adapter v1 (skeleton)

AIAdapterインターフェースの最小実装。
Handshake → Commission → Execute → ACK の4ステップの形を確定するための
スケルトンであり、実際のOpenAI API呼び出しは行わない。
"""
from __future__ import annotations
from datetime import datetime, timezone

from .adapter_interface import AIAdapter


class OpenAIAdapter(AIAdapter):
    AI_ID = "GPT"

    def __init__(self):
        self._session_id: str | None = None

    def handshake(self, scope: str) -> dict:
        self._session_id = f"session_{self.AI_ID}_{datetime.now(timezone.utc).timestamp():.0f}"
        return {
            "status": "ok",
            "trust_level": "trial",
            "session_id": self._session_id,
            "capabilities": ["CAP_STATE_READ"],
            "scope": scope,
        }

    def receive_commission(self, commission: dict) -> bool:
        return bool(commission.get("commission_id"))

    def execute(self, commission: dict) -> dict:
        return {
            "commission_id": commission.get("commission_id"),
            "output": f"[{self.AI_ID}] executed: {commission.get('task', '')}",
        }

    def ack(self, result: dict) -> dict:
        return {
            "ai_id": self.AI_ID,
            "commission_id": result.get("commission_id"),
            "status": "ok",
            "result": result,
            "responded_at": datetime.now(timezone.utc).isoformat(),
        }
