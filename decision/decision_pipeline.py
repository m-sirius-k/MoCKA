"""
MoCKA 3.0 — Decision Layer
decision_pipeline.py

責務:
  Semantic Layer (SemanticPipeline) と Decision Engine を統合する単一窓口。

  処理フロー:
    text/context -> SemanticPipeline -> SemanticResult
                  -> DecisionEngine   -> DecisionResult

  Decision Layerは実行を行わない。常に required_governance_check=True を
  伴うDecisionResultを返し、最終判断はGovernance Layer(GL1-7)に委ねる。
"""

import sys
from pathlib import Path

# semantic/ をimport可能にする(decision/とsemantic/は兄弟ディレクトリ)
_SEMANTIC_DIR = Path(__file__).resolve().parent.parent / "semantic"
if str(_SEMANTIC_DIR) not in sys.path:
    sys.path.insert(0, str(_SEMANTIC_DIR))

from semantic_pipeline import SemanticPipeline  # noqa: E402

from decision_engine import DecisionEngine  # noqa: E402
from decision_model import DecisionResult  # noqa: E402


class DecisionPipeline:
    """Decision Layerの統一エントリポイント。"""

    def __init__(self, semantic_pipeline: SemanticPipeline = None, decision_engine: DecisionEngine = None):
        self._semantic_pipeline = semantic_pipeline or SemanticPipeline()
        self._decision_engine = decision_engine or DecisionEngine()

    def process(self, text: str, context: dict = None) -> DecisionResult:
        """
        テキストとコンテキストからDecisionResultを生成する。

        Args:
            text: 利用者からの要求テキスト。
            context: ContextAnalyzerが参照するコンテキスト辞書。

        Returns:
            DecisionResult: selected_action/alternatives/priority_score/
            risk_score/confidence/rationale/required_governance_check。
        """
        semantic_result = self._semantic_pipeline.process(text, context)
        return self._decision_engine.decide(semantic_result)

    def decide_from_semantic(self, semantic_result) -> DecisionResult:
        """既に得たSemanticResultからDecisionResultを生成する(Semantic Layerを再実行しない)。"""
        return self._decision_engine.decide(semantic_result)
