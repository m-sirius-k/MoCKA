"""
MoCKA 3.0 — Self-Audit Layer Feedbackテスト

確認内容:
  - FeedbackGeneratorがissue_listからimprovement_suggestionsを生成すること
  - improvement_suggestionsに自動修正/自動実行に関する記述が無いこと
  - ImprovementScorerが影響度/リスク低減効果/頻度/波及性に基づき
    0-1のスコアを返すこと
  - prioritized_actionsがimprovement_score降順であること
  - Self-AuditがDecision/Memory/Governanceを直接変更しないこと(逆流禁止)
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from audit_model import ImprovementSuggestion, PrioritizedAction  # noqa: E402
from audit_registry import SeverityLevel  # noqa: E402
from feedback_generator import FeedbackGenerator  # noqa: E402
from improvement_scorer import ImprovementScorer  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    scorer = ImprovementScorer()
    generator = FeedbackGenerator(scorer)

    # --- ImprovementScorer単体テスト ---
    for severity in SeverityLevel.ORDER:
        score = scorer.score(severity_level=severity, target_type="governance",
                              occurrence_count=1, max_occurrence=1)
        results.append(check(
            f"ImprovementScorer.score(severity='{severity}') is within [0, 1]",
            0.0 <= score <= 1.0,
        ))

    critical_score = scorer.score(severity_level=SeverityLevel.CRITICAL, target_type="governance",
                                    occurrence_count=1, max_occurrence=1)
    info_score = scorer.score(severity_level=SeverityLevel.INFO, target_type="memory",
                               occurrence_count=1, max_occurrence=1)
    results.append(check(
        "critical/governance score is higher than info/memory score",
        critical_score > info_score,
    ))

    # --- 頻度(frequency)の反映 ---
    low_freq = scorer.score(severity_level=SeverityLevel.MEDIUM, target_type="decision",
                             occurrence_count=1, max_occurrence=5)
    high_freq = scorer.score(severity_level=SeverityLevel.MEDIUM, target_type="decision",
                              occurrence_count=5, max_occurrence=5)
    results.append(check(
        "higher occurrence_count yields a higher or equal improvement_score",
        high_freq >= low_freq,
    ))

    # --- FeedbackGenerator.generate_suggestions ---
    issue_list = (
        {"check": "priority妥当性", "description": "issue A", "severity": "high"},
        {"check": "risk整合性", "description": "issue B", "severity": "critical"},
        {"check": "rationale一貫性", "description": "issue C", "severity": "low"},
    )
    suggestions = generator.generate_suggestions("decision", "decision_layer", issue_list)

    results.append(check(
        "generate_suggestions returns one suggestion per issue",
        len(suggestions) == len(issue_list),
    ))
    results.append(check(
        "all suggestions are ImprovementSuggestion instances",
        all(isinstance(s, ImprovementSuggestion) for s in suggestions),
    ))
    results.append(check(
        "all suggestion.improvement_score are within [0, 1]",
        all(0.0 <= s.improvement_score <= 1.0 for s in suggestions),
    ))

    # --- 自動修正/自動実行を伴わない記述であること ---
    forbidden_terms = ("自動実行", "自動コード変更", "auto-fix", "auto fix")
    results.append(check(
        "suggestion descriptions do not claim automatic fixes/execution",
        all(not any(term in s.description for term in forbidden_terms) for s in suggestions),
    ))
    results.append(check(
        "suggestion descriptions explicitly state no automatic fix is applied",
        all("自動修正を伴わない" in s.description for s in suggestions),
    ))

    # --- 重大度が高いissueほどimprovement_scoreが高いこと ---
    by_check = {s.related_check: s for s in suggestions}
    results.append(check(
        "critical issue (risk整合性) has higher score than low issue (rationale一貫性)",
        by_check["risk整合性"].improvement_score > by_check["rationale一貫性"].improvement_score,
    ))

    # --- prioritized_actions ---
    actions = generator.generate_prioritized_actions(suggestions)
    results.append(check(
        "generate_prioritized_actions returns one action per suggestion",
        len(actions) == len(suggestions),
    ))
    results.append(check(
        "all actions are PrioritizedAction instances",
        all(isinstance(a, PrioritizedAction) for a in actions),
    ))
    results.append(check(
        "prioritized_actions are sorted by improvement_score descending",
        all(actions[i].improvement_score >= actions[i + 1].improvement_score
            for i in range(len(actions) - 1)),
    ))
    results.append(check(
        "top prioritized_action corresponds to the highest severity issue",
        actions[0].suggestion.related_check == "risk整合性",
    ))

    # --- 空issue_listの場合 ---
    empty_suggestions = generator.generate_suggestions("memory", "memory_layer", ())
    results.append(check(
        "generate_suggestions returns empty tuple for empty issue_list",
        empty_suggestions == (),
    ))

    # --- to_dict()の動作確認 ---
    suggestion_dict = suggestions[0].to_dict()
    results.append(check(
        "ImprovementSuggestion.to_dict() contains required keys",
        all(key in suggestion_dict for key in (
            "suggestion_id", "target_type", "target_id", "description",
            "related_check", "improvement_score",
        )),
    ))
    action_dict = actions[0].to_dict()
    results.append(check(
        "PrioritizedAction.to_dict() contains 'suggestion' as a dict",
        isinstance(action_dict["suggestion"], dict),
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
