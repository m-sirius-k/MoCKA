"""
MoCKA 3.0 — Feedback Loop
decision_tuner.py

責務:
  Decision Layerへの改善提案(risk scoring補正/priority scoring再配分/
  rationale構造改善)を生成する。

  本モジュールはDecisionResult/decision_registry等を変更せず、
  提案(dict)を返すのみ。
"""


class DecisionTuner:
    """Decision Layerに対する改善提案を生成するTuner。"""

    def propose(self, issue) -> dict:
        """issue.checkに応じてDecision Layerへの改善提案を生成する。"""
        if issue.check == "risk整合性":
            return self._risk_scoring_correction(issue)
        if issue.check == "priority妥当性":
            return self._priority_redistribution(issue)
        if issue.check == "rationale一貫性":
            return self._rationale_structure_improvement(issue)

        return {
            "tuning_type": "none",
            "description": f"未対応のcheck '{issue.check}' のためDecision Tuner提案なし。",
        }

    # ------------------------------------------------------------------
    def _risk_scoring_correction(self, issue) -> dict:
        """risk_analyzerのスコアリング補正提案。"""
        return {
            "tuning_type": "risk_scoring_correction",
            "module": "decision/risk_analyzer.py",
            "description": (
                f"{issue.description} を踏まえ、risk_score >= 0.6の場合に"
                f"risk_factorsが必ず1件以上記録されるよう、RiskAnalyzer.analyze()"
                f"の条件分岐を見直すことを提案する。"
            ),
        }

    def _priority_redistribution(self, issue) -> dict:
        """priority_scorerの重み再配分提案。"""
        return {
            "tuning_type": "priority_scoring_redistribution",
            "module": "decision/priority_scorer.py",
            "description": (
                f"{issue.description} を踏まえ、intent_importance/"
                f"context_strength/dependency/urgency/intent_clarityの"
                f"重み配分を再評価し、selected_actionがDecision Registryの"
                f"候補と整合するよう調整することを提案する。"
            ),
        }

    def _rationale_structure_improvement(self, issue) -> dict:
        """rationale文の構造改善提案。"""
        return {
            "tuning_type": "rationale_structure_improvement",
            "module": "decision/decision_engine.py",
            "description": (
                f"{issue.description} を踏まえ、rationale文に"
                f"selected_action/priority_score/risk_scoreの3要素を"
                f"必ず明記するテンプレートへ改善することを提案する。"
            ),
        }
