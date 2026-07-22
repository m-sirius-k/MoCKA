"""
MoCKA Hub -- ChatGPT Adapter (R01)
====================================
Author : Claude (R02)
Date   : 2026-07-22
Purpose: ChatGPT の出力を MoCKA Event 形式に変換する

ChatGPT の特性:
  - 長い会話 / ファイル / URL / 推論結果を出力する
  - Notion や GitHub への直接アクセスは不可
  - 役割: Audit / Design Review / Paper Sub
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatGPTOutput:
    content: str
    role: str = "R01"
    session_id: Optional[str] = None


class ChatGPTAdapter:
    """
    ChatGPT の出力を MoCKA Event 形式に変換する。
    """

    ROLE = "R01"
    ALLOWED_ACTIONS = ["audit", "review", "comment"]

    def to_mocka_event(self, output: ChatGPTOutput) -> dict:
        return {
            "what_type": "collaboration",
            "who_actor": f"GPT (R01) session={output.session_id or 'unknown'}",
            "short_summary": output.content[:200] if output.content else "",
            "ai_actor": "chatgpt",
            "channel_type": "human_relay",  # Human Gate 経由
        }

    def validate_authority(self, action: str) -> bool:
        allowed = {
            "read": True,
            "audit": True,
            "write_event": False,   # Human Gate 経由のみ
            "write_decision": False,
            "delete": False,
        }
        return allowed.get(action, False)


# TODO (くろこ): ChatGPT Plugin / API 経由の受信処理を追加
# TODO (くろこ): 審査結果 (Approve/Reject) の MoCKA Event 変換を追加
