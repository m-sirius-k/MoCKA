"""
MoCKA Institution Gateway Hub -- Policy Engine
===============================================
Author : Claude (R02) + GPT (R01)
Date   : 2026-07-22
Purpose: 公開レベル (A/B/C) の定義と判定

Visibility Levels:
  A = public    -> GitHub Pages / Public Docs
  B = internal  -> Notion only
  C = restricted -> Never published
"""

from enum import Enum
from typing import Optional


class Visibility(Enum):
    PUBLIC = "A"
    INTERNAL = "B"
    RESTRICTED = "C"


# コンテンツタイプごとのデフォルト公開レベル
CONTENT_POLICY: dict[str, Visibility] = {
    # Level A -- Public
    "architecture":    Visibility.PUBLIC,
    "agent_roles":     Visibility.PUBLIC,
    "papers":          Visibility.PUBLIC,
    "products":        Visibility.PUBLIC,
    "faq":             Visibility.PUBLIC,
    "overview":        Visibility.PUBLIC,

    # Level B -- Internal (Notion only)
    "living_context":  Visibility.INTERNAL,
    "decision_summary":Visibility.INTERNAL,
    "event_stats":     Visibility.INTERNAL,
    "project_status":  Visibility.INTERNAL,
    "timeline":        Visibility.INTERNAL,

    # Level C -- Restricted (never published)
    "decision_detail": Visibility.RESTRICTED,
    "event_detail":    Visibility.RESTRICTED,
    "evidence_raw":    Visibility.RESTRICTED,
    "sqlite":          Visibility.RESTRICTED,
    "mcp_config":      Visibility.RESTRICTED,
    "api_keys":        Visibility.RESTRICTED,
    "internal_paths":  Visibility.RESTRICTED,
    "operation_logs":  Visibility.RESTRICTED,
}


class PolicyEngine:
    """公開レベルを判定し、配信先を決定する"""

    def get_visibility(self, content_type: str) -> Visibility:
        return CONTENT_POLICY.get(content_type, Visibility.RESTRICTED)

    def can_publish(self, content_type: str, destination: str) -> bool:
        """
        destination: 'public' | 'notion' | 'restricted'
        """
        v = self.get_visibility(content_type)
        if destination == "public":
            return v == Visibility.PUBLIC
        if destination == "notion":
            return v in (Visibility.PUBLIC, Visibility.INTERNAL)
        return False

    def get_destinations(self, content_type: str) -> list[str]:
        v = self.get_visibility(content_type)
        if v == Visibility.PUBLIC:
            return ["public", "notion"]
        if v == Visibility.INTERNAL:
            return ["notion"]
        return []


# TODO (くろこ): PolicyEngine を MoCKA Publisher と接続する
# TODO (くろこ): Policy をMoCKA Core の governance テーブルで管理できるようにする
