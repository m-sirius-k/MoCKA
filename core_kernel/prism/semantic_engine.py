"""
MoCKA Core Kernel — prism.semantic_engine

責務:
  単一Eventの意味解釈を行い、SemanticAnnotationを生成する。

  これは「意味の確定」ではなく「Prismによる解釈」である。
  Core Kernelへの書き込みは行わない。
"""

import uuid

from .models import SemanticAnnotation

_KNOWN_EVENT_TYPES = {
    "change_start": ("lifecycle", "変更作業の開始", 0.7),
    "change_done": ("lifecycle", "変更作業の完了", 0.7),
    "context_capture": ("context", "状況の記録", 0.6),
    "context_restore": ("context", "状況の復元", 0.6),
    "module_registered": ("registry", "モジュールの登録", 0.6),
    "module_loaded": ("registry", "モジュールの読み込み", 0.6),
    "lifecycle_changed": ("lifecycle", "状態遷移", 0.6),
}


class SemanticEngine:
    """EventからSemanticAnnotationを生成する。"""

    def annotate(self, event: dict) -> SemanticAnnotation:
        event_type = event.get("event_type", "")
        category, meaning, confidence = self._classify(event_type)

        explanation, confidence = self._refine(event, category, meaning, confidence)

        return SemanticAnnotation(
            annotation_id=str(uuid.uuid4()),
            event_id=event.get("event_id", ""),
            meaning=meaning,
            category=category,
            confidence=confidence,
            explanation=explanation,
            metadata={"event_type": event_type},
        )

    def annotate_many(self, events):
        return tuple(self.annotate(event) for event in events)

    @staticmethod
    def _classify(event_type: str):
        """event_typeから(category, meaning, confidence)の初期値を決定する。"""
        if event_type in _KNOWN_EVENT_TYPES:
            return _KNOWN_EVENT_TYPES[event_type]

        if event_type.endswith("_start"):
            return ("lifecycle", f"{event_type} の開始", 0.4)
        if event_type.endswith("_done") or event_type.endswith("_completed"):
            return ("lifecycle", f"{event_type} の完了", 0.4)
        if "context" in event_type:
            return ("context", f"{event_type} に関する状況情報", 0.4)

        return ("unknown", "未分類のイベント", 0.2)

    @staticmethod
    def _refine(event: dict, category: str, meaning: str, confidence: float):
        """payload/metadataの充実度に応じてconfidenceとexplanationを調整する。"""
        event_type = event.get("event_type", "")
        payload = event.get("payload") or {}

        explanation = f"event_type='{event_type}' に基づき category='{category}' と判定"

        if not payload:
            confidence = max(0.1, confidence - 0.2)
            explanation += "（payloadが空のため確度を下げた）"
        elif len(payload) >= 2:
            confidence = min(1.0, confidence + 0.1)
            explanation += "（payload情報が豊富なため確度を上げた）"

        target_module = event.get("target_module")
        if target_module:
            explanation += f"（target_module='{target_module}' を確認）"

        return explanation, round(confidence, 2)
