"""
MoCKA 3.0 — Decision Layer
decision_engine.py

責務:
  SemanticResultを入力として、DecisionResultを生成するコアエンジン。

  - Intent解釈        : SemanticResult.intent / candidates を読む
  - 候補生成          : decision_registryのdefault_action/alternative_actionsから生成
  - 優先順位付け      : PriorityScorer
  - リスク評価統合    : RiskAnalyzer
  - 推奨アクション生成: 最高優先度の候補をselected_actionとする

  Decision Layerは実行を行わない(非破壊)。
  常に required_governance_check=True を伴うDecisionResultを返し、
  最終判断はGovernance Layer(GL1-7)に委ねる。
"""

from decision_model import Alternative, DecisionResult
from decision_registry import get_decision_profile
from priority_scorer import PriorityScorer
from risk_analyzer import RiskAnalyzer


class DecisionEngine:
    """SemanticResult -> DecisionResult のコアエンジン。"""

    def __init__(self, priority_scorer: PriorityScorer = None, risk_analyzer: RiskAnalyzer = None):
        self._priority_scorer = priority_scorer or PriorityScorer()
        self._risk_analyzer = risk_analyzer or RiskAnalyzer()

    def decide(self, semantic_result) -> DecisionResult:
        profile = get_decision_profile(semantic_result.intent.key)

        priority_score = self._priority_scorer.score(semantic_result, profile)
        risk_score, risk_factors = self._risk_analyzer.analyze(semantic_result, profile)

        # selected_action: 主Intentの推奨アクション
        selected_action = profile.default_action

        # alternatives: 主Intentの代替アクション + 第2候補以降のIntentの推奨アクション
        alternatives = []
        for alt_text in profile.alternative_actions:
            alternatives.append(Alternative(
                action=alt_text,
                priority_score=round(priority_score * 0.8, 4),
                risk_score=risk_score,
            ))

        for candidate in semantic_result.candidates[1:]:
            alt_profile = get_decision_profile(candidate.key)
            alt_priority = self._priority_scorer.score(semantic_result, alt_profile)
            alt_risk, _ = self._risk_analyzer.analyze(semantic_result, alt_profile)
            alternatives.append(Alternative(
                action=alt_profile.default_action,
                priority_score=alt_priority,
                risk_score=alt_risk,
            ))

        rationale = self._build_rationale(
            semantic_result, profile, priority_score, risk_score,
        )

        return DecisionResult(
            selected_action=selected_action,
            alternatives=tuple(alternatives),
            priority_score=priority_score,
            risk_score=risk_score,
            confidence=semantic_result.confidence,
            rationale=rationale,
            required_governance_check=True,
            risk_factors=risk_factors,
        )

    @staticmethod
    def _build_rationale(semantic_result, profile, priority_score, risk_score) -> str:
        return (
            f"Intent='{semantic_result.intent.label_en}' "
            f"(confidence={semantic_result.confidence}) を "
            f"action_profile='{profile.action_profile}' として解釈。"
            f"priority_score={priority_score}, risk_score={risk_score}。"
            f"Context summary: {semantic_result.context_summary.summary_text}。"
            f"最終的な実行可否はGovernance Layerの判断に委ねる。"
        )
