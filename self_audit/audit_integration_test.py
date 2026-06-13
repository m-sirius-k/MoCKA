"""
MoCKA 3.0 — Self-Audit Layer 統合テスト

確認内容:
  - Self-Audit Layerが独立モジュールとして動作すること
  - Semantic/Decision/Memory/Governanceの全層をAuditできること
  - AuditReportが生成されること
  - Feedback(improvement_suggestions/prioritized_actions)が生成されること
  - Improvement Scoringが0-1の範囲で機能すること
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from audit_model import AuditReport, PrioritizedAction  # noqa: E402
from audit_pipeline import AuditPipeline  # noqa: E402
from audit_registry import SeverityLevel, TargetType  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    pipeline = AuditPipeline()
    audit_result = pipeline.run_full_audit()

    # --- 全層が評価対象として含まれる ---
    for target_type in TargetType.ALL:
        if target_type == TargetType.DECISION:
            reports = audit_result["decision"]
            results.append(check(
                f"decision layer produces at least 1 AuditReport",
                len(reports) >= 1,
            ))
            for report in reports:
                results.append(check(
                    f"decision report '{report.target_id}' is AuditReport",
                    isinstance(report, AuditReport),
                ))
        else:
            report = audit_result[target_type]
            results.append(check(
                f"{target_type} layer produces an AuditReport",
                isinstance(report, AuditReport),
            ))

    # --- AuditReportの基本フィールド検証 ---
    semantic_report = audit_result["semantic"]
    results.append(check(
        "semantic AuditReport.target_type == 'semantic'",
        semantic_report.target_type == TargetType.SEMANTIC,
    ))
    results.append(check(
        "semantic AuditReport.evaluation_score is within [0, 1]",
        0.0 <= semantic_report.evaluation_score <= 1.0,
    ))
    results.append(check(
        "semantic AuditReport.severity_level is a known SeverityLevel",
        semantic_report.severity_level in SeverityLevel.ORDER,
    ))

    governance_report = audit_result["governance"]
    results.append(check(
        "governance AuditReport.target_type == 'governance'",
        governance_report.target_type == TargetType.GOVERNANCE,
    ))
    results.append(check(
        "governance AuditReport.evaluation_score is within [0, 1]",
        0.0 <= governance_report.evaluation_score <= 1.0,
    ))

    memory_report = audit_result["memory"]
    results.append(check(
        "memory AuditReport.target_type == 'memory'",
        memory_report.target_type == TargetType.MEMORY,
    ))

    # --- to_dict()の動作確認 ---
    semantic_dict = semantic_report.to_dict()
    results.append(check(
        "AuditReport.to_dict() contains required keys",
        all(key in semantic_dict for key in (
            "audit_id", "target_type", "target_id", "evaluation_score",
            "issue_list", "strength_list", "improvement_suggestions", "severity_level",
        )),
    ))

    # --- prioritized_actionsの検証 ---
    prioritized_actions = audit_result["prioritized_actions"]
    results.append(check(
        "prioritized_actions is a tuple",
        isinstance(prioritized_actions, tuple),
    ))
    if prioritized_actions:
        results.append(check(
            "all prioritized_actions are PrioritizedAction instances",
            all(isinstance(a, PrioritizedAction) for a in prioritized_actions),
        ))
        results.append(check(
            "prioritized_actions improvement_score is within [0, 1]",
            all(0.0 <= a.improvement_score <= 1.0 for a in prioritized_actions),
        ))
        results.append(check(
            "prioritized_actions are sorted by improvement_score descending",
            all(prioritized_actions[i].improvement_score >= prioritized_actions[i + 1].improvement_score
                for i in range(len(prioritized_actions) - 1)),
        ))

    # --- to_dict()(Pipeline全体)の動作確認 ---
    full_dict = AuditPipeline.to_dict(audit_result)
    results.append(check(
        "AuditPipeline.to_dict() contains all 5 top-level keys",
        set(full_dict.keys()) == {"semantic", "decision", "memory", "governance", "prioritized_actions"},
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
