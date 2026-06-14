"""
MoCKA Core Kernel — prism.analyzer

責務:
  Prismの公開エントリポイント。

  公開API:
    - analyze(event)
    - analyze_many(events)

  この2つ以外のメソッドを公開APIとして追加してはならない。
"""

from dataclasses import dataclass

from .interfaces import AnalyzerInterface
from .models import CognitiveState, Context, Observation, SemanticAnnotation
from .pipeline import PrismPipeline


@dataclass(frozen=True)
class AnalysisResult:
    """analyze / analyze_many の戻り値。"""

    annotations: tuple
    context: Context
    cognitive_state: CognitiveState
    observation: Observation


class PrismAnalyzer(AnalyzerInterface):
    """Prism認知層の公開エントリポイント。"""

    def __init__(self, registry=None, lifecycle=None, type_registry=None):
        """
        Args:
            registry: core_store.ModuleRegistry (読み取り専用利用、省略可)
            lifecycle: core_store.LifecycleManager (読み取り専用利用、省略可)
            type_registry: event_contracts.EventTypeRegistry (省略可)
        """
        self._pipeline = PrismPipeline(
            registry=registry,
            lifecycle=lifecycle,
            type_registry=type_registry,
        )

    def analyze(self, event: dict) -> AnalysisResult:
        return self.analyze_many([event])

    def analyze_many(self, events) -> AnalysisResult:
        result = self._pipeline.run(events)
        return AnalysisResult(
            annotations=result.annotations,
            context=result.context,
            cognitive_state=result.cognitive_state,
            observation=result.observation,
        )
