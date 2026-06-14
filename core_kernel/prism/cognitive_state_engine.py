"""
MoCKA Core Kernel — prism.cognitive_state_engine

責務:
  SemanticAnnotation群・Contextから、現在の認知状態(CognitiveState)を判定する。

  判定は簡易ルールベースのstub実装であり、将来的な高度化を妨げないよう
  公開APIは「annotations, context を受け取り CognitiveState を返す」に限定する。
"""

from .models import CognitiveState, CognitiveStateValue


class CognitiveStateEngine:
    """SemanticAnnotation群とContextからCognitiveStateを判定する。"""

    UNKNOWN_RATIO_THRESHOLD = 0.5

    def evaluate(self, annotations, context) -> CognitiveState:
        if not annotations:
            return CognitiveState(
                state=CognitiveStateValue.INCOMPLETE,
                confidence=0.3,
                reason="解析対象のEventが存在しない",
                metadata={},
            )

        unknown_count = sum(
            1 for annotation in annotations if annotation.category == "unknown"
        )
        unknown_ratio = unknown_count / len(annotations)

        if unknown_ratio >= self.UNKNOWN_RATIO_THRESHOLD:
            return CognitiveState(
                state=CognitiveStateValue.UNCERTAIN,
                confidence=0.4,
                reason="未分類のEventが多数を占める",
                metadata={"unknown_ratio": unknown_ratio},
            )

        categories = {annotation.category for annotation in annotations}
        if "lifecycle" in categories and len(categories) > 1:
            return CognitiveState(
                state=CognitiveStateValue.LEARNING,
                confidence=0.6,
                reason="複数カテゴリのイベントから状況を学習中",
                metadata={"categories": sorted(categories)},
            )

        avg_confidence = sum(a.confidence for a in annotations) / len(annotations)

        return CognitiveState(
            state=CognitiveStateValue.STABLE,
            confidence=avg_confidence,
            reason="既知パターンに基づく安定した解釈",
            metadata={"categories": sorted(categories)},
        )
