"""
MoCKA Core Kernel — prism.semantic_engine

責務:
  単一Eventの意味解釈を行い、SemanticAnnotationを生成する。

  これは「意味の確定」ではなく「Prismによる解釈」である。
  Core Kernelへの書き込みは行わない。
"""

import uuid

from .models import SemanticAnnotation


class SemanticEngine:
    """EventからSemanticAnnotationを生成する。"""

    def annotate(self, event: dict) -> SemanticAnnotation:
        event_type = event.get("event_type", "")
        category, meaning, confidence = self._classify(event_type)

        return SemanticAnnotation(
            annotation_id=str(uuid.uuid4()),
            event_id=event.get("event_id", ""),
            meaning=meaning,
            category=category,
            confidence=confidence,
            explanation=f"event_type='{event_type}' に基づく初期分類",
            metadata={"event_type": event_type},
        )

    def annotate_many(self, events):
        return tuple(self.annotate(event) for event in events)

    @staticmethod
    def _classify(event_type: str):
        """event_typeから(category, meaning, confidence)を決定する。

        現段階ではstub実装であり、固定的な簡易マッピングのみを行う。
        """
        mapping = {
            "change_start": ("lifecycle", "変更作業の開始", 0.6),
            "change_done": ("lifecycle", "変更作業の完了", 0.6),
            "context_capture": ("context", "状況の記録", 0.5),
            "context_restore": ("context", "状況の復元", 0.5),
            "module_registered": ("registry", "モジュールの登録", 0.5),
            "module_loaded": ("registry", "モジュールの読み込み", 0.5),
            "lifecycle_changed": ("lifecycle", "状態遷移", 0.5),
        }
        return mapping.get(event_type, ("unknown", "未分類のイベント", 0.2))
