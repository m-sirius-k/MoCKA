"""
MoCKA 3.0 — Feedback Loop
feedback_registry.py

責務:
  Feedback Loopが扱うfeedback_type・target_layer・impact_level・
  優先度ルール・安全制約を一元管理するRegistry。

  Self-Audit Layerと同様、本Registryは「分類・優先度付け・安全制約の
  定義」のみを行い、実行や即時反映のルールは含まない。
"""

import sys
from pathlib import Path

_SELF_AUDIT_DIR = Path(__file__).resolve().parent.parent / "self_audit"
if str(_SELF_AUDIT_DIR) not in sys.path:
    sys.path.insert(0, str(_SELF_AUDIT_DIR))

from audit_registry import SeverityLevel, TargetType  # noqa: E402


class TargetLayer:
    """Feedback Proposalの適用対象層。"""

    DECISION = "decision"
    MEMORY = "memory"
    SEMANTIC = "semantic"

    ALL = (DECISION, MEMORY, SEMANTIC)


class FeedbackType:
    """Feedback Proposalの種別。"""

    WEIGHT_ADJUSTMENT = "weight_adjustment"
    RATIONALE_IMPROVEMENT = "rationale_improvement"
    MEMORY_REINFORCEMENT = "memory_reinforcement"
    MEMORY_DECAY = "memory_decay"
    REUSE_WEIGHT_ADJUSTMENT = "reuse_weight_adjustment"
    INTENT_THRESHOLD_ADJUSTMENT = "intent_threshold_adjustment"
    CONTEXT_IMPROVEMENT = "context_improvement"
    REGISTRY_CANDIDATE = "registry_candidate"


# impact_level (severity_levelと同一の語彙を使用する)
IMPACT_LEVELS = SeverityLevel.ORDER


# severity_level -> confidence(0-1)
# severityが高い(=問題が明確)ほど、提案の確信度を高く見積もる。
CONFIDENCE_BY_SEVERITY = {
    SeverityLevel.CRITICAL: 0.95,
    SeverityLevel.HIGH: 0.85,
    SeverityLevel.MEDIUM: 0.7,
    SeverityLevel.LOW: 0.5,
    SeverityLevel.INFO: 0.3,
}


# Self-Audit Layerのcheck名 -> (target_layer, feedback_type) の分類ルール。
# Governance Layerのcheckはtarget_layerを持たない(=Feedback対象外)。
# これは「Governance変更禁止」「逆流禁止」を分類レベルで保証するための定義である。
CHECK_CLASSIFICATION = {
    # Decision Layer
    "priority妥当性": (TargetLayer.DECISION, FeedbackType.WEIGHT_ADJUSTMENT),
    "risk整合性": (TargetLayer.DECISION, FeedbackType.WEIGHT_ADJUSTMENT),
    "rationale一貫性": (TargetLayer.DECISION, FeedbackType.RATIONALE_IMPROVEMENT),
    # Memory Layer
    "再利用性": (TargetLayer.MEMORY, FeedbackType.REUSE_WEIGHT_ADJUSTMENT),
    "一貫性": (TargetLayer.MEMORY, FeedbackType.MEMORY_REINFORCEMENT),
    "ノイズ率": (TargetLayer.MEMORY, FeedbackType.MEMORY_DECAY),
    # Semantic Layer (軽微・提案のみ)
    "意図分類精度": (TargetLayer.SEMANTIC, FeedbackType.INTENT_THRESHOLD_ADJUSTMENT),
    "context補完妥当性": (TargetLayer.SEMANTIC, FeedbackType.CONTEXT_IMPROVEMENT),
}


# feedback_type -> 優先度の基礎値(0-1)。Improvement Scorer同様、
# severityとの組み合わせでexpected_impactを算出する際の重みとして用いる。
PRIORITY_RULES = {
    FeedbackType.WEIGHT_ADJUSTMENT: 0.8,
    FeedbackType.RATIONALE_IMPROVEMENT: 0.5,
    FeedbackType.MEMORY_REINFORCEMENT: 0.6,
    FeedbackType.MEMORY_DECAY: 0.6,
    FeedbackType.REUSE_WEIGHT_ADJUSTMENT: 0.5,
    FeedbackType.INTENT_THRESHOLD_ADJUSTMENT: 0.5,
    FeedbackType.CONTEXT_IMPROVEMENT: 0.4,
    FeedbackType.REGISTRY_CANDIDATE: 0.4,
}


# 安全制約: Feedback Loopが絶対に行わないこと。
# テスト(feedback_safety_test.py)から参照され、Proposal/Pipelineの
# 出力がこれらに該当しないことを検証する。
SAFETY_CONSTRAINTS = (
    "no_automatic_code_modification",
    "no_governance_change",
    "no_execution_logic_change",
    "no_immediate_apply",
    "no_memory_deletion",
)


def get_classification(check: str):
    """
    check名からFeedback分類(target_layer, feedback_type)を返す。
    Governance Layerのcheck等、分類対象外の場合はNoneを返す。
    """
    return CHECK_CLASSIFICATION.get(check)


def confidence_for_severity(severity: str) -> float:
    """severity_levelからconfidence(0-1)を返す。"""
    return CONFIDENCE_BY_SEVERITY.get(severity, 0.3)


def priority_for_feedback_type(feedback_type: str) -> float:
    """feedback_typeから優先度基礎値(0-1)を返す。"""
    return PRIORITY_RULES.get(feedback_type, 0.3)


def is_feedback_target(target_type: str) -> bool:
    """AuditReport.target_typeがFeedback対象層かどうかを返す(Governanceは対象外)。"""
    return target_type != TargetType.GOVERNANCE
