"""
MoCKA Core Kernel — prism.models.observation

責務:
  Prismによる観測結果(推論支援用)を表す不変データ構造。

  Action/Command/Workflow情報は持たない。
  recommendationは「示唆」であり、実行可能なコマンドではない。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Observation:
    """Prismの観測結果。Workflow制御や実行指示は含まない。"""

    observation_id: str
    timestamp: str
    confidence: float
    finding: str = ""
    evidence_event_ids: tuple = field(default_factory=tuple)
    recommendation: str = ""
    risk_level: str = "unknown"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "finding": self.finding,
            "evidence_event_ids": list(self.evidence_event_ids),
            "recommendation": self.recommendation,
            "risk_level": self.risk_level,
            "metadata": dict(self.metadata),
        }
