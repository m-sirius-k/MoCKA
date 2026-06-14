"""
MoCKA Core Kernel — prism.cognitive_state_engine

責務:
  SemanticAnnotation群・Contextから、現在の認知状態(CognitiveState)を判定する。

  判定はルールベースであり、公開APIは
  「annotations, context を受け取り CognitiveState を返す」に限定する。

  状態の種類:
    - STABLE: 単一カテゴリで、確度が十分高い
    - UNSTABLE: 複数カテゴリが混在し、解釈が一貫していない
    - UNCERTAIN: 未分類(unknown)のイベントが多数を占める
    - INCOMPLETE: 解析対象のイベントが存在しない
    - CONFLICT: 関係性(relationships)に矛盾が検出される
"""

from .models import CognitiveState, CognitiveStateValue

UNKNOWN_RATIO_THRESHOLD = 0.5


class CognitiveStateEngine:
    """SemanticAnnotation群とContextからCognitiveStateを判定する。"""

    def evaluate(self, annotations, context) -> CognitiveState:
        if not annotations:
            return CognitiveState(
                state=CognitiveStateValue.INCOMPLETE,
                confidence=0.3,
                reason="解析対象のEventが存在しない",
                metadata={},
            )

        conflict = self._detect_conflict(context)
        if conflict is not None:
            return conflict

        unknown_count = sum(
            1 for annotation in annotations if annotation.category == "unknown"
        )
        unknown_ratio = unknown_count / len(annotations)

        if unknown_ratio >= UNKNOWN_RATIO_THRESHOLD:
            return CognitiveState(
                state=CognitiveStateValue.UNCERTAIN,
                confidence=round(0.5 - unknown_ratio * 0.2, 2),
                reason="未分類のEventが多数を占める",
                metadata={"unknown_ratio": unknown_ratio},
            )

        categories = {annotation.category for annotation in annotations}
        avg_confidence = sum(a.confidence for a in annotations) / len(annotations)

        if len(categories) > 1:
            return CognitiveState(
                state=CognitiveStateValue.UNSTABLE,
                confidence=round(avg_confidence * 0.8, 2),
                reason="複数カテゴリのイベントが混在し、解釈が一貫していない",
                metadata={"categories": sorted(categories)},
            )

        return CognitiveState(
            state=CognitiveStateValue.STABLE,
            confidence=round(avg_confidence, 2),
            reason="既知パターンに基づく安定した解釈",
            metadata={"categories": sorted(categories)},
        )

    @staticmethod
    def _detect_conflict(context):
        """relationshipsに循環するcausality関係が含まれる場合、CONFLICTとする。"""
        causality_edges = {
            (r["from"], r["to"])
            for r in context.relationships
            if r.get("type") == "causality"
        }

        for (a, b) in causality_edges:
            if (b, a) in causality_edges:
                return CognitiveState(
                    state=CognitiveStateValue.CONFLICT,
                    confidence=0.5,
                    reason="循環するcausality関係が検出された",
                    metadata={"conflicting_pair": [a, b]},
                )

        return None
