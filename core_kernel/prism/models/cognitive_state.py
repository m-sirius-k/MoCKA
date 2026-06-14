"""
MoCKA Core Kernel — prism.models.cognitive_state

責務:
  Prismが認識した「現在の認知状態」を表す不変データ構造。
"""

from dataclasses import dataclass, field

from .schema_version import PRISM_OUTPUT_SCHEMA_VERSION


class CognitiveStateValue:
    """CognitiveState.state の候補値。"""

    STABLE = "STABLE"
    UNSTABLE = "UNSTABLE"
    UNCERTAIN = "UNCERTAIN"
    INCOMPLETE = "INCOMPLETE"
    CONFLICT = "CONFLICT"

    ALL = (STABLE, UNSTABLE, UNCERTAIN, INCOMPLETE, CONFLICT)


@dataclass(frozen=True)
class CognitiveState:
    """Prismが認識した認知状態。"""

    state: str
    confidence: float
    reason: str = ""
    metadata: dict = field(default_factory=dict)
    version: str = PRISM_OUTPUT_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "confidence": self.confidence,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "version": self.version,
        }
