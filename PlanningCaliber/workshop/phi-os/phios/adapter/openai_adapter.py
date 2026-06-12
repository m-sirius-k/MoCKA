# phi_os/adapter/openai_adapter.py
"""OpenAIAdapter v0 — APIは呼ばない（実行はexecute()内でのみ将来呼び出す）"""
from __future__ import annotations
from datetime import datetime, timezone

from adapter.adapter_interface import AIAdapter


class OpenAIAdapter(AIAdapter):
    AI_ID = "openai"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def handshake(self, scope: str = "institution_state") -> dict:
        return {
            "status": "ok",
            "ai_id": self.AI_ID,
            "trust_level": "trial",
            "capabilities": ["CAP_STATE_READ", "taxonomy_validation"],
            "scope": scope,
        }

    def receive_commission(self, commission: dict) -> bool:
        return "task" in commission

    def execute(self, commission: dict) -> dict:
        # v0: 実際のOpenAI API呼び出しは行わない（テストではモック化想定）
        return {"result": f"[openai] executed: {commission.get('task', '')}"}

    def ack(self, result: dict) -> dict:
        return {
            "ok": True,
            "actor": self.AI_ID,
            "result": result,
            "responded_at": datetime.now(timezone.utc).isoformat(),
        }
