"""
MoCKA Core Kernel — prism.models.cognitive_state

責務:
  Prismが認識した「現在の認知状態」を表す不変データ構造。
"""

from dataclasses import dataclass, field


class CognitiveStateValue:
    """CognitiveState.state の候補値。"""

    STABLE = "STABLE"
    UNCERTAIN = "UNCERTAIN"
    INCOMPLETE = "INCOMPLETE"
    CONFLICT = "CONFLICT"
    LEARNING = "LEARNING"

    ALL = (STABLE, UNCERTAIN, INCOMPLETE, CONFLICT, LEARNING)


@dataclass(frozen=True)
class CognitiveState:
    """Prismが認識した認知状態。"""

    state: str
    confidence: float
    reason: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "confidence": self.confidence,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }
