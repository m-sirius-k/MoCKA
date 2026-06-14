"""
MoCKA Core Kernel — prism.models.semantic_annotation

責務:
  単一EventへのSemantic Analysisの結果を表す不変データ構造。
  保存処理・配送処理は持たない(データ構造のみ)。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SemanticAnnotation:
    """単一Eventに対する意味付け。"""

    annotation_id: str
    event_id: str
    meaning: str
    category: str
    confidence: float
    explanation: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "annotation_id": self.annotation_id,
            "event_id": self.event_id,
            "meaning": self.meaning,
            "category": self.category,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "metadata": dict(self.metadata),
        }
