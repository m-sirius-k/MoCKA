"""
MoCKA Hub -- Gemini Adapter
=============================
Author : Claude (R02)
Date   : 2026-07-22
Purpose: Gemini の出力を MoCKA Event 形式に変換する

Gemini の特性:
  - 調査 / Web 検索が中心
  - 役割: Adversarial Reviewer
  - 論文の弱点指摘・反論生成
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GeminiOutput:
    content: str
    search_results: list[dict] = None
    session_id: Optional[str] = None


class GeminiAdapter:
    """
    Gemini の出力を MoCKA Event 形式に変換する。
    """

    ROLE = "Adversarial Reviewer"

    def to_mocka_event(self, output: GeminiOutput) -> dict:
        return {
            "what_type": "collaboration",
            "who_actor": f"Gemini (Adversarial) session={output.session_id or 'unknown'}",
            "short_summary": output.content[:200] if output.content else "",
            "ai_actor": "gemini",
            "channel_type": "human_relay",
        }

    def validate_authority(self, action: str) -> bool:
        allowed = {
            "read": True,
            "challenge": True,
            "review": True,
            "write_event": False,
            "write_decision": False,
            "delete": False,
        }
        return allowed.get(action, False)


# TODO (くろこ): Gemini API 経由の受信処理を追加
# TODO (くろこ): 反論レポートの Evidence 変換を追加
