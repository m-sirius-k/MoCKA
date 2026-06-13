"""
MoCKA 3.0 — Decision Layer
risk_analyzer.py

責務:
  意思決定におけるリスクを 0-1 のスコアと要因リストで評価する。

評価対象:
  - Governance違反可能性   (action_profile=write_heavyはGL7 Dry Run対象 = 違反可能性が相対的に高い)
  - 副作用リスク           (decision_registry.DecisionProfile.base_risk)
  - 未知動作可能性         (Intentがunknown、または候補間のconfidenceが近接=曖昧)
  - Context不確実性        (ContextSummaryが空に近いほど不確実性が高い)

出力:
  risk_score (0-1), risk_factors[] (説明文のリスト)。
  実行可否の判断(Governance Layerの責務)は行わない。
"""

from decision_registry import DecisionProfile

# 各評価軸の重み(合計 1.0)
_WEIGHTS = {
    "base_risk": 0.40,
    "governance_violation": 0.20,
    "unknown_behavior": 0.20,
    "context_uncertainty": 0.20,
}

# action_profileごとのGovernance違反可能性(GL7 Default Deny: READ_ONLY_TOOLS以外はDry Run対象)
_GOVERNANCE_RISK_BY_PROFILE = {
    "write_heavy": 0.8,
    "verification_first": 0.3,
    "analysis_heavy": 0.2,
    "read_heavy": 0.1,
}


class RiskAnalyzer:
    """SemanticResultとDecisionProfileからリスクを評価するAnalyzer。"""

    def analyze(self, semantic_result, profile: DecisionProfile):
        """
        Returns:
            (risk_score: float, risk_factors: tuple[str])
        """
        risk_factors = list(profile.risk_factors)

        base_risk = profile.base_risk

        governance_risk = _GOVERNANCE_RISK_BY_PROFILE.get(profile.action_profile, 0.5)

        unknown_behavior = self._unknown_behavior_risk(semantic_result)
        if semantic_result.intent.key == "unknown":
            risk_factors.append("Intentが特定できないため、未知動作のリスクがある")
        elif unknown_behavior > 0.5:
            risk_factors.append("Intent候補のconfidenceが近接しており、意図が曖昧")

        context_uncertainty = self._context_uncertainty(semantic_result.context_summary)
        if context_uncertainty > 0.5:
            risk_factors.append("コンテキスト情報が不足しており、不確実性が高い")

        risk_score = (
            base_risk * _WEIGHTS["base_risk"]
            + governance_risk * _WEIGHTS["governance_violation"]
            + unknown_behavior * _WEIGHTS["unknown_behavior"]
            + context_uncertainty * _WEIGHTS["context_uncertainty"]
        )
        risk_score = round(min(1.0, max(0.0, risk_score)), 4)

        return risk_score, tuple(risk_factors)

    @staticmethod
    def _unknown_behavior_risk(semantic_result) -> float:
        """Intentがunknown、または候補confidenceが近接している場合のリスク(0-1)。"""
        if semantic_result.intent.key == "unknown":
            return 1.0

        candidates = semantic_result.candidates
        if len(candidates) < 2:
            return 1.0 - semantic_result.confidence

        gap = candidates[0].confidence - candidates[1].confidence
        return round(min(1.0, max(0.0, 1.0 - gap)), 4)

    @staticmethod
    def _context_uncertainty(context_summary) -> float:
        """ContextSummaryが空に近いほど不確実性(0-1)が高くなる。"""
        signals = (
            bool(context_summary.phase),
            bool(context_summary.active_task),
            bool(context_summary.recent_events),
            bool(context_summary.conversation_flow),
        )
        filled = sum(1 for s in signals if s)
        return round(1.0 - (filled / len(signals)), 4)
