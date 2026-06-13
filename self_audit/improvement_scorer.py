"""
MoCKA 3.0 — Self-Audit Layer
improvement_scorer.py

責務:
  改善提案(ImprovementSuggestion)に対し、以下4軸の重み付き合計で
  0-1のimprovement_scoreを算出する:
    - 影響度 (impact)
    - リスク低減効果 (risk_reduction)
    - 頻度 (frequency)
    - システム全体への波及性 (ripple)

  本モジュールはスコアリングのみを行い、提案内容や対象層を
  変更しない。
"""

from audit_registry import SeverityLevel


# severity_level -> 影響度/リスク低減効果の基礎スコア
_SEVERITY_IMPACT = {
    SeverityLevel.CRITICAL: 1.0,
    SeverityLevel.HIGH: 0.8,
    SeverityLevel.MEDIUM: 0.5,
    SeverityLevel.LOW: 0.3,
    SeverityLevel.INFO: 0.1,
}

# target_type -> システム全体への波及性の基礎スコア
# (Governance/Decisionの問題はSemantic/Memoryより波及範囲が広い)
_RIPPLE_BY_TARGET = {
    "governance": 1.0,
    "decision": 0.7,
    "memory": 0.5,
    "semantic": 0.5,
}

_WEIGHTS = {
    "impact": 0.35,
    "risk_reduction": 0.30,
    "frequency": 0.15,
    "ripple": 0.20,
}


class ImprovementScorer:
    """ImprovementSuggestionにimprovement_score(0-1)を付与するScorer。"""

    def score(self, severity_level: str, target_type: str, occurrence_count: int = 1,
              max_occurrence: int = 1) -> float:
        """
        Args:
            severity_level: issueのseverity_level
            target_type: TargetType (semantic/decision/memory/governance)
            occurrence_count: 同種issueの出現回数
            max_occurrence: 今回のAudit実行における出現回数の最大値(正規化用)

        Returns:
            improvement_score (0.0 - 1.0)
        """
        impact = _SEVERITY_IMPACT.get(severity_level, 0.3)
        risk_reduction = _SEVERITY_IMPACT.get(severity_level, 0.3)
        ripple = _RIPPLE_BY_TARGET.get(target_type, 0.5)

        if max_occurrence > 0:
            frequency = min(1.0, occurrence_count / max_occurrence)
        else:
            frequency = 0.0

        score = (
            impact * _WEIGHTS["impact"]
            + risk_reduction * _WEIGHTS["risk_reduction"]
            + frequency * _WEIGHTS["frequency"]
            + ripple * _WEIGHTS["ripple"]
        )
        return round(min(1.0, max(0.0, score)), 4)
