"""
MoCKA 3.0 — Decision Layer
priority_scorer.py

責務:
  複数候補(Intent候補 / アクション候補)の優先順位を 0-1 のスコアで数値化する。

評価軸:
  - Intent重要度       (decision_registry.DecisionProfile.priority_weight)
  - コンテキスト強度    (ContextSummaryに含まれる情報量)
  - 依存関係           (action_profileがverification_first/analysis_heavyの場合、
                         先行作業への依存があるとみなし優先度をやや下げる)
  - 緊急度(推定)        (action_profileがwrite_heavy/fixの場合は緊急度を高めに推定)
  - ユーザー意図明確度  (SemanticResultのconfidence、候補間のスコア差)

出力:
  0.0 - 1.0 のスコア。判断(実行可否)は行わない。
"""

from decision_registry import DecisionProfile

# 各評価軸の重み(合計 1.0)
_WEIGHTS = {
    "intent_importance": 0.30,
    "context_strength": 0.20,
    "dependency": 0.15,
    "urgency": 0.15,
    "intent_clarity": 0.20,
}

# action_profileごとの緊急度(推定)
_URGENCY_BY_PROFILE = {
    "write_heavy": 0.7,
    "verification_first": 0.5,
    "analysis_heavy": 0.4,
    "read_heavy": 0.3,
}

# action_profileごとの依存関係スコア(高いほど「先行作業への依存が小さい」=動きやすい)
_DEPENDENCY_BY_PROFILE = {
    "read_heavy": 0.9,
    "analysis_heavy": 0.7,
    "verification_first": 0.6,
    "write_heavy": 0.5,
}


class PriorityScorer:
    """SemanticResultとDecisionProfileから優先度スコアを算出するScorer。"""

    def score(self, semantic_result, profile: DecisionProfile) -> float:
        intent_importance = profile.priority_weight

        context_strength = self._context_strength(semantic_result.context_summary)

        dependency = _DEPENDENCY_BY_PROFILE.get(profile.action_profile, 0.5)

        urgency = _URGENCY_BY_PROFILE.get(profile.action_profile, 0.5)

        intent_clarity = self._intent_clarity(semantic_result)

        score = (
            intent_importance * _WEIGHTS["intent_importance"]
            + context_strength * _WEIGHTS["context_strength"]
            + dependency * _WEIGHTS["dependency"]
            + urgency * _WEIGHTS["urgency"]
            + intent_clarity * _WEIGHTS["intent_clarity"]
        )
        return round(min(1.0, max(0.0, score)), 4)

    @staticmethod
    def _context_strength(context_summary) -> float:
        """ContextSummaryに含まれる情報量から、コンテキスト強度(0-1)を推定する。"""
        signals = (
            bool(context_summary.phase),
            bool(context_summary.active_task),
            bool(context_summary.recent_events),
            bool(context_summary.conversation_flow),
        )
        return sum(1 for s in signals if s) / len(signals)

    @staticmethod
    def _intent_clarity(semantic_result) -> float:
        """SemanticResultのconfidenceと候補間のスコア差から、意図の明確さ(0-1)を推定する。"""
        confidence = semantic_result.confidence
        candidates = semantic_result.candidates

        if len(candidates) < 2:
            return confidence

        gap = candidates[0].confidence - candidates[1].confidence
        return round(min(1.0, max(0.0, (confidence + gap) / 2)), 4)
