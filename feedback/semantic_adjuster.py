"""
MoCKA 3.0 — Feedback Loop
semantic_adjuster.py

責務:
  Semantic Layerに対する改善提案(intent分類精度改善/context補完強化/
  registry追加候補)を生成する。

  実装変更は禁止。本モジュールは提案文字列・候補情報を返すのみであり、
  semantic_registry / intent_classifier / context_analyzer のいずれも
  変更しない。
"""


class SemanticAdjuster:
    """Semantic Layerに対する改善提案(軽微・提案のみ)を生成するAdjuster。"""

    def propose(self, issue) -> dict:
        """issue.checkに応じてSemantic Layerへの改善提案を生成する。"""
        if issue.check == "意図分類精度":
            return self._intent_classification_improvement(issue)
        if issue.check == "context補完妥当性":
            return self._context_completion_improvement(issue)

        return {
            "adjustment_type": "none",
            "description": f"未対応のcheck '{issue.check}' のためSemantic Adjuster提案なし。",
        }

    # ------------------------------------------------------------------
    def _intent_classification_improvement(self, issue) -> dict:
        """intent分類精度改善 + registry追加候補の提案。"""
        return {
            "adjustment_type": "intent_classification_improvement",
            "module": "semantic/intent_classifier.py",
            "registry_candidate": True,
            "description": (
                f"{issue.description} を踏まえ、誤分類されたテキストの"
                f"キーワードをsemantic_registry.INTENT_REGISTRYの該当intentの"
                f"keywordsに追加する候補として記録することを提案する"
                f"(Registryへの実際の追加は別途レビューを要する)。"
            ),
        }

    def _context_completion_improvement(self, issue) -> dict:
        """context補完強化の提案。"""
        return {
            "adjustment_type": "context_completion_improvement",
            "module": "semantic/context_analyzer.py",
            "registry_candidate": False,
            "description": (
                f"{issue.description} を踏まえ、contextに"
                f"phase/active_task/recent_events/conversation_flowが"
                f"与えられた場合のsummary_text生成ロジックを見直し、"
                f"空文字列となるケースを減らすことを提案する。"
            ),
        }
