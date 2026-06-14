"""
MoCKA Core Kernel — prism

Prism: Cognition Layer

責務:
  Eventを解釈し、Context / SemanticAnnotation / CognitiveState / Observation
  を生成する。Core Kernelへの書き込み・Workflow制御・Action実行は行わない。

公開API:
  PrismAnalyzer.analyze(event)
  PrismAnalyzer.analyze_many(events)
"""

from .analyzer import AnalysisResult, PrismAnalyzer
from .exceptions import InvalidEventError, PipelineError, PrismError
from .models import (
    CognitiveState,
    CognitiveStateValue,
    Context,
    Observation,
    SemanticAnnotation,
)
from .provider import CAPABILITY_COGNITION, PrismProvider
from .version import PRISM_VERSION

__all__ = [
    "PrismAnalyzer",
    "AnalysisResult",
    "PrismProvider",
    "CAPABILITY_COGNITION",
    "PrismError",
    "InvalidEventError",
    "PipelineError",
    "Context",
    "Observation",
    "SemanticAnnotation",
    "CognitiveState",
    "CognitiveStateValue",
    "PRISM_VERSION",
]
