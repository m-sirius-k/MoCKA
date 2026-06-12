# phios/registry/decision_rules.py
"""Decision Rules — 意味→Actionのルール定義（データ駆動）"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionRule:
    """1つのルール定義"""
    condition_impact: str | None   # "critical" | "system" | "local" | None(any)
    condition_intent: str | None   # "recover" | "govern" | "validate" | None(any)
    action_type: str                # "escalate" | "delegate" | "notify" | "seal" | "noop"
    target: str                     # "human_gate" | "mock" | "verify_all" | "ledger"
    priority_base: int              # 1〜3


# ルールテーブル（優先順位順・最初にマッチしたルールが適用される）
DECISION_RULES: list[DecisionRule] = [
    # criticalは最優先でhuman_gateへ
    DecisionRule("critical", None, "escalate", "human_gate", 3),
    # recover intentはmockで復旧試行
    DecisionRule(None, "recover", "delegate", "mock", 2),
    # govern intentはhuman_gateへ通知
    DecisionRule(None, "govern", "notify", "human_gate", 2),
    # validate intentはverify_allトリガー
    DecisionRule(None, "validate", "seal", "verify_all", 1),
    # その他はnoop
    DecisionRule(None, None, "noop", "ledger", 1),
]


def match_rule(impact: str, intent: str) -> DecisionRule:
    """impactとintentに最初にマッチするルールを返す"""
    for rule in DECISION_RULES:
        impact_match = rule.condition_impact is None or rule.condition_impact == impact
        intent_match = rule.condition_intent is None or rule.condition_intent == intent
        if impact_match and intent_match:
            return rule
    return DECISION_RULES[-1]  # fallback: noop
