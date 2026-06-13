"""
MoCKA 3.0 — Semantic Layer
intent_classifier.py

責務:
  入力テキストを「意味単位(Intent)」で分類する。
  文字列そのものではなく、Semantic Registryに登録された
  IntentDefinition(目的)を返す。

  - 単語境界(\\b)マッチでキーワードをカウントし、複数候補をスコア付きで返す。
  - 安全性/実行可否の判断は行わない(Governance Layerの責務外)。
"""

import re
from dataclasses import dataclass

from semantic_registry import INTENT_REGISTRY, UNKNOWN_INTENT, IntentDefinition


@dataclass(frozen=True)
class IntentMatch:
    """1つのIntent候補とその確信度。"""

    intent: IntentDefinition
    confidence: float       # 0.0 - 1.0
    matched_keywords: tuple


def _keyword_pattern(keyword: str) -> re.Pattern:
    # 日本語キーワードは単語境界(\b)が効かないため、英数字キーワードのみ
    # \bを付与する。日本語キーワードは部分一致のまま大文字小文字無視で扱う。
    if re.fullmatch(r"[A-Za-z0-9_;: ]+", keyword):
        escaped = re.escape(keyword.strip())
        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return re.compile(re.escape(keyword), re.IGNORECASE)


class IntentClassifier:
    """テキストを意味単位(Intent)で分類するClassifier。"""

    def __init__(self, registry=INTENT_REGISTRY):
        self._registry = registry

    def classify(self, text: str, top_k: int = 3) -> tuple:
        """
        テキストを分類し、確信度の高い順に IntentMatch のtupleを返す。

        マッチが1件も無い場合は UNKNOWN_INTENT (confidence=0.0) を含む
        1件のタプルを返す。
        """
        if not text:
            return (IntentMatch(UNKNOWN_INTENT, 0.0, ()),)

        matches = []
        for definition in self._registry:
            matched = tuple(
                kw for kw in definition.keywords
                if _keyword_pattern(kw).search(text)
            )
            if not matched:
                continue
            confidence = min(1.0, len(matched) / max(1, len(definition.keywords)) * 2)
            matches.append(IntentMatch(definition, confidence, matched))

        if not matches:
            return (IntentMatch(UNKNOWN_INTENT, 0.0, ()),)

        matches.sort(key=lambda m: m.confidence, reverse=True)
        return tuple(matches[:top_k])
