"""
MoCKA 3.0 — Self-Audit Layer
audit_registry.py

責務:
  Self-Auditの評価ルール・スコア閾値・severity定義・層別チェック項目を
  一元管理するRegistry。Self-Audit Layer自身は「評価・分析・スコアリング・
  改善提案生成」のみを担当し、Governance/Decision/Memory/Semanticの
  ロジックや内容には変更を加えない(読み取り専用)。
"""


class TargetType:
    """audit対象となる層の種別。"""

    SEMANTIC = "semantic"
    DECISION = "decision"
    MEMORY = "memory"
    GOVERNANCE = "governance"

    ALL = (SEMANTIC, DECISION, MEMORY, GOVERNANCE)


class SeverityLevel:
    """issueの重大度。"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    ORDER = (INFO, LOW, MEDIUM, HIGH, CRITICAL)


# evaluation_score(0-1) -> severity_level のしきい値。
# score が高い(=問題が少ない)ほどseverityは低い。
# (score_min, severity_level) を score降順で評価する。
SCORE_THRESHOLDS = (
    (0.85, SeverityLevel.INFO),
    (0.65, SeverityLevel.LOW),
    (0.45, SeverityLevel.MEDIUM),
    (0.25, SeverityLevel.HIGH),
    (0.0, SeverityLevel.CRITICAL),
)


def score_to_severity(score: float) -> str:
    """evaluation_score(0-1)からseverity_levelを決定する。"""
    score = max(0.0, min(1.0, score))
    for threshold, severity in SCORE_THRESHOLDS:
        if score >= threshold:
            return severity
    return SeverityLevel.CRITICAL


# 層別チェック項目(評価軸)。audit_analyzerが参照するドキュメント用定義。
LAYER_CHECKS = {
    TargetType.DECISION: (
        "priority妥当性",
        "risk整合性",
        "rationale一貫性",
    ),
    TargetType.MEMORY: (
        "再利用性",
        "一貫性",
        "ノイズ率",
    ),
    TargetType.SEMANTIC: (
        "意図分類精度",
        "context補完妥当性",
    ),
    TargetType.GOVERNANCE: (
        "Fail Closed維持",
        "bypass検出",
        "異常ログ",
    ),
}


def get_layer_checks(target_type: str) -> tuple:
    """target_typeに対応するチェック項目タプルを返す(未知の場合は空タプル)。"""
    return LAYER_CHECKS.get(target_type, ())


def all_target_types() -> tuple:
    return TargetType.ALL
