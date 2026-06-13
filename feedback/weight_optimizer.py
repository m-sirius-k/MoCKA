"""
MoCKA 3.0 — Feedback Loop
weight_optimizer.py

責務:
  Decision/Memory/Semanticの「重み調整案」を生成する。

  本モジュールは調整案(parameter/current_value/suggested_delta/direction/
  reason)を辞書として返すのみであり、実際のRegistry/Pipelineの値を
  変更しない(非破壊・提案のみ)。
"""

# 調整幅の基礎値。severityが高いほど調整幅を大きくする。
_DELTA_BY_SEVERITY = {
    "critical": 0.10,
    "high": 0.07,
    "medium": 0.05,
    "low": 0.02,
    "info": 0.01,
}


class WeightOptimizer:
    """各層の重み調整案を生成するOptimizer。"""

    # ------------------------------------------------------------------
    # Decision Layer
    # ------------------------------------------------------------------
    def decision_weight_adjustment(self, issue) -> dict:
        """
        priority_scorer / risk_analyzerの重み調整案を生成する。

        issue.check が "priority妥当性" の場合は priority_scorer側、
        "risk整合性" の場合は risk_analyzer側のweightを対象とする。
        """
        delta = _DELTA_BY_SEVERITY.get(issue.severity, 0.02)

        if issue.check == "priority妥当性":
            return {
                "module": "decision/priority_scorer.py",
                "parameter": "intent_clarity",
                "current_weight": 0.20,
                "suggested_delta": +delta,
                "direction": "increase",
                "reason": (
                    f"{issue.description} のため、intent_clarityの重みを"
                    f"+{delta:.2f}増加させ、priority_scoreの妥当性を高める案。"
                ),
            }

        if issue.check == "risk整合性":
            return {
                "module": "decision/risk_analyzer.py",
                "parameter": "governance_violation",
                "current_weight": 0.20,
                "suggested_delta": +delta,
                "direction": "increase",
                "reason": (
                    f"{issue.description} のため、governance_violationの重みを"
                    f"+{delta:.2f}増加させ、risk_scoreとrisk_factorsの整合性を高める案。"
                ),
            }

        return {
            "module": "decision",
            "parameter": "unknown",
            "current_weight": None,
            "suggested_delta": 0.0,
            "direction": "none",
            "reason": f"未対応のcheck '{issue.check}' のため調整案なし。",
        }

    # ------------------------------------------------------------------
    # Memory Layer
    # ------------------------------------------------------------------
    def memory_weight_adjustment(self, issue) -> dict:
        """
        memory_retrieverの relevance_score重み / recency減衰の調整案を生成する。
        """
        delta = _DELTA_BY_SEVERITY.get(issue.severity, 0.02)

        if issue.check == "再利用性":
            return {
                "module": "memory/memory_retriever.py",
                "parameter": "intent_match",
                "current_weight": 0.40,
                "suggested_delta": +delta,
                "direction": "increase",
                "reason": (
                    f"{issue.description} のため、intent_matchの重みを"
                    f"+{delta:.2f}増加させ、再利用可能な記憶が優先的に"
                    f"検索されるようにする案。"
                ),
            }

        if issue.check == "ノイズ率":
            return {
                "module": "memory/memory_retriever.py",
                "parameter": "recency_decay",
                "current_weight": 0.15,
                "suggested_delta": -delta,
                "direction": "decrease",
                "reason": (
                    f"{issue.description} のため、recencyの重みを"
                    f"-{delta:.2f}減少させ、重複・低価値な新規記憶が"
                    f"過剰に優先されないようにする案。"
                ),
            }

        return {
            "module": "memory",
            "parameter": "unknown",
            "current_weight": None,
            "suggested_delta": 0.0,
            "direction": "none",
            "reason": f"未対応のcheck '{issue.check}' のため調整案なし。",
        }

    # ------------------------------------------------------------------
    # Semantic Layer (軽微・提案のみ)
    # ------------------------------------------------------------------
    def semantic_threshold_adjustment(self, issue) -> dict:
        """
        intent confidence thresholdの調整案を生成する(提案のみ)。
        """
        delta = _DELTA_BY_SEVERITY.get(issue.severity, 0.02)

        if issue.check == "意図分類精度":
            return {
                "module": "semantic/intent_classifier.py",
                "parameter": "confidence_threshold",
                "current_weight": None,
                "suggested_delta": -delta,
                "direction": "decrease",
                "reason": (
                    f"{issue.description} のため、confidence_thresholdを"
                    f"-{delta:.2f}下げ、上位候補をより柔軟に採用できるか"
                    f"検討する案(実装変更は別途レビューを要する)。"
                ),
            }

        return {
            "module": "semantic",
            "parameter": "unknown",
            "current_weight": None,
            "suggested_delta": 0.0,
            "direction": "none",
            "reason": f"未対応のcheck '{issue.check}' のため調整案なし。",
        }
