"""
MoCKA 3.0 — Self-Audit Layer
feedback_generator.py

責務:
  AuditEngineが算出したissue_listから、改善提案(ImprovementSuggestion)と
  優先度付きアクション(PrioritizedAction)を生成する。

  絶対禁止:
    - 自動修正 (automatic fixes)
    - 自動コード変更 (automatic code changes)
    - 自動実行 (automatic execution)

  出力は improvement_suggestions / prioritized_actions のみであり、
  いずれも「提案」であってDecision/Governance/Memory/Semanticへの
  直接的な書き込みは一切行わない(逆流禁止)。
"""

from collections import Counter

from audit_model import ImprovementSuggestion, PrioritizedAction
from improvement_scorer import ImprovementScorer


class FeedbackGenerator:
    """issue_listからImprovementSuggestion/PrioritizedActionを生成するGenerator。"""

    def __init__(self, scorer: ImprovementScorer = None):
        self._scorer = scorer or ImprovementScorer()

    def generate_suggestions(self, target_type: str, target_id: str, issue_list: tuple) -> tuple:
        """
        issue_list(list[dict], 各要素にcheck/description/severityを含む)から
        improvement_score付きのImprovementSuggestionのtupleを生成する。

        Returns:
            tuple[ImprovementSuggestion]
        """
        if not issue_list:
            return ()

        check_counts = Counter(issue.get("check", "unknown") for issue in issue_list)
        max_occurrence = max(check_counts.values()) if check_counts else 1

        suggestions = []
        for index, issue in enumerate(issue_list):
            check = issue.get("check", "unknown")
            description = issue.get("description", "")
            severity = issue.get("severity", "info")

            score = self._scorer.score(
                severity_level=severity,
                target_type=target_type,
                occurrence_count=check_counts[check],
                max_occurrence=max_occurrence,
            )

            suggestions.append(ImprovementSuggestion(
                suggestion_id=f"SUGGEST_{target_type}_{target_id}_{index:03d}",
                target_type=target_type,
                target_id=target_id,
                description=self._suggest_text(check, description),
                related_check=check,
                improvement_score=score,
            ))
        return tuple(suggestions)

    def generate_prioritized_actions(self, suggestions: tuple) -> tuple:
        """
        improvement_score降順に並べたPrioritizedActionのtupleを返す。
        """
        actions = []
        for suggestion in suggestions:
            actions.append(PrioritizedAction(
                suggestion=suggestion,
                improvement_score=suggestion.improvement_score,
                rationale=(
                    f"check='{suggestion.related_check}' に関する改善提案。"
                    f"improvement_score={suggestion.improvement_score} に基づき優先度を決定。"
                ),
            ))
        actions.sort(key=lambda a: a.improvement_score, reverse=True)
        return tuple(actions)

    @staticmethod
    def _suggest_text(check: str, description: str) -> str:
        """issueの内容から改善提案文を組み立てる(提案のみ、自動修正は行わない)。"""
        return (
            f"[{check}] {description} について、原因を分析し改善案を検討することを推奨する"
            f"(本提案は自動修正を伴わない)。"
        )
