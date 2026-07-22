"""
MoCKA Hub -- Claude Adapter (R02)
==================================
Author : Claude (R02)
Date   : 2026-07-22
Purpose: Claude の出力を MoCKA Event 形式に変換する

Claude の特性:
  - MCP ツール経由で MoCKA と直接通信できる
  - コード / パッチ / ドキュメント出力が中心
  - Notion MCP との連携あり
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaudeOutput:
    content: str
    tool_calls: list[dict]
    session_id: Optional[str] = None


class ClaudeAdapter:
    """
    Claude の出力を MoCKA Event 形式に変換する。
    """

    ROLE = "R02"
    ALLOWED_WHAT_TYPES = [
        "claude_mcp",
        "DECISION_APPROVED",
        "collaboration",
        "record",
    ]

    def to_mocka_event(self, output: ClaudeOutput) -> dict:
        """
        Claude の出力を MoCKA events テーブルの形式に変換する。
        """
        return {
            "what_type": "claude_mcp",
            "who_actor": f"Claude (R02) session={output.session_id or 'unknown'}",
            "short_summary": output.content[:200] if output.content else "",
            "ai_actor": "claude",
            "channel_type": "mcp",
        }

    def validate_authority(self, action: str) -> bool:
        """
        Claude (R02) が実行してよい操作かを確認する。
        """
        allowed = {
            "read": True,
            "write_event": True,
            "write_decision": False,  # Human Gate 必須
            "delete": False,
            "push_main": False,       # 直接push禁止
        }
        return allowed.get(action, False)


# TODO (くろこ): MoCKA MCP startup protocol との連携
# TODO (くろこ): Notion MCP 出力の変換も追加
