"""
MoCKA Core Kernel — prism.pipeline

責務:
  Prismの処理段階を固定順序で実行する。

  FIXED ORDER:
    Normalize -> Semantic Analysis -> Correlation -> Context Build
    -> State Recognition -> Observation Build

  この順序はPrismの契約であり、変更してはならない。
"""

from dataclasses import dataclass, field

from core_kernel.event_contracts import validate_event

from .cognitive_state_engine import CognitiveStateEngine
from .context_engine import ContextEngine
from .correlation_engine import CorrelationEngine
from .exceptions import InvalidEventError
from .models import CognitiveState, Context, Observation, SemanticAnnotation
from .observation_engine import ObservationEngine
from .semantic_engine import SemanticEngine


@dataclass(frozen=True)
class PipelineResult:
    """PrismPipelineの実行結果。"""

    annotations: tuple = field(default_factory=tuple)
    context: Context = None
    cognitive_state: CognitiveState = None
    observation: Observation = None


class PrismPipeline:
    """固定順序でPrismの各Engineを実行する。"""

    def __init__(self, registry=None, lifecycle=None, type_registry=None):
        self._semantic_engine = SemanticEngine()
        self._correlation_engine = CorrelationEngine()
        self._context_engine = ContextEngine(registry=registry, lifecycle=lifecycle)
        self._cognitive_state_engine = CognitiveStateEngine()
        self._observation_engine = ObservationEngine()
        self._type_registry = type_registry

    def run(self, events) -> PipelineResult:
        normalized = self._normalize(events)

        annotations = self._semantic_engine.annotate_many(normalized)

        relationships = self._correlation_engine.correlate(normalized)

        context = self._context_engine.build(normalized, annotations, relationships)

        cognitive_state = self._cognitive_state_engine.evaluate(annotations, context)

        observation = self._observation_engine.observe(context, cognitive_state)

        return PipelineResult(
            annotations=annotations,
            context=context,
            cognitive_state=cognitive_state,
            observation=observation,
        )

    def _normalize(self, events):
        """EventがEvent Contractに準拠していることを検証する。

        Pipelineは検証のみを行い、Eventの内容を変更しない。
        """
        normalized = []
        for event in events:
            result = validate_event(event, type_registry=self._type_registry)
            if not result.valid:
                raise InvalidEventError(
                    f"event_id={event.get('event_id')!r} の検証に失敗: {result.errors}"
                )
            normalized.append(event)
        return tuple(normalized)
