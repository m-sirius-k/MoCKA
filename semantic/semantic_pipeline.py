"""
MoCKA 3.0 — Semantic Layer
semantic_pipeline.py

責務:
  Intent Classifier / Context Analyzer / Semantic Registry を統合し、
  統一形式のSemanticResultを生成する単一窓口。

  Semantic LayerはGovernance Layer(GL1-7)とは独立した層であり、
  安全性・実行可否・品質保証の判断は行わない。
  本Pipelineの出力(SemanticResult)は「意味理解の結果」であり、
  実行判断は将来のDecision Layerに委ねる。
"""

from context_analyzer import ContextAnalyzer
from intent_classifier import IntentClassifier
from semantic_registry import get_intent
from semantic_result import IntentCandidate, SemanticResult


class SemanticPipeline:
    """Semantic Layerの統一エントリポイント。"""

    def __init__(self, classifier: IntentClassifier = None, analyzer: ContextAnalyzer = None):
        self._classifier = classifier or IntentClassifier()
        self._analyzer = analyzer or ContextAnalyzer()

    def process(self, text: str, context: dict = None) -> SemanticResult:
        """
        テキストとコンテキストからSemanticResultを生成する。

        Args:
            text: 利用者からの要求テキスト。
            context: 直前イベント・会話の流れ・現在フェーズ・Active Task等
                     (ContextAnalyzerが参照するキー: phase, active_task,
                      recent_events, conversation_flow)。

        Returns:
            SemanticResult: Intent/Confidence/ContextSummary/Related Topics/
            Recommended Actionを含む統一出力。
        """
        matches = self._classifier.classify(text)
        top_match = matches[0]

        candidates = tuple(
            IntentCandidate(
                key=match.intent.key,
                label_ja=match.intent.label_ja,
                label_en=match.intent.label_en,
                confidence=match.confidence,
            )
            for match in matches
        )

        context_summary = self._analyzer.analyze(context)

        top_intent = get_intent(top_match.intent.key)
        related_topics = tuple(top_intent.related_topics)

        return SemanticResult(
            intent=candidates[0],
            confidence=top_match.confidence,
            context_summary=context_summary,
            related_topics=related_topics,
            recommended_action=top_intent.recommended_action,
            candidates=candidates,
        )
