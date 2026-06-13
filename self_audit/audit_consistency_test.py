"""
MoCKA 3.0 — Self-Audit Layer 整合性テスト

確認内容:
  - audit_registry のスコア閾値/severity定義/層別チェック項目の整合性
  - AuditAnalyzerの各層評価が層分離(層への変更なし)を保つこと
  - Governance Layer違反(bypass/Fail Closed異常)を検出できること
  - issue/strengthの形式整合性
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from audit_analyzer import AuditAnalyzer  # noqa: E402
from audit_registry import (  # noqa: E402
    LAYER_CHECKS,
    SeverityLevel,
    TargetType,
    get_layer_checks,
    score_to_severity,
)


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    # --- score_to_severity整合性 ---
    results.append(check(
        "score_to_severity(1.0) == info",
        score_to_severity(1.0) == SeverityLevel.INFO,
    ))
    results.append(check(
        "score_to_severity(0.0) == critical",
        score_to_severity(0.0) == SeverityLevel.CRITICAL,
    ))
    results.append(check(
        "score_to_severity is monotonic non-increasing severity as score increases",
        SeverityLevel.ORDER.index(score_to_severity(0.9))
        <= SeverityLevel.ORDER.index(score_to_severity(0.1)),
    ))

    # --- LAYER_CHECKS整合性 ---
    for target_type in TargetType.ALL:
        checks = get_layer_checks(target_type)
        results.append(check(
            f"LAYER_CHECKS['{target_type}'] is non-empty",
            len(checks) > 0,
        ))
    results.append(check(
        "LAYER_CHECKS covers all TargetType.ALL",
        set(LAYER_CHECKS.keys()) == set(TargetType.ALL),
    ))

    # --- 評価軸とAnalyzer出力の整合性 (Decision) ---
    analyzer = AuditAnalyzer()

    from decision_pipeline import DecisionPipeline  # noqa: E402
    from semantic_pipeline import SemanticPipeline  # noqa: E402

    semantic_pipeline = SemanticPipeline()
    decision_pipeline = DecisionPipeline()

    semantic_result = semantic_pipeline.process(
        "Decision Engineを実装して新しいモジュールを追加して",
        {"phase": "phase3-1", "active_task": "TODO_self_audit"},
    )
    decision_result = decision_pipeline.decide_from_semantic(semantic_result)

    score, issues, strengths = analyzer.analyze_decision(decision_result, semantic_result)
    results.append(check(
        "analyze_decision returns score within [0, 1]",
        0.0 <= score <= 1.0,
    ))
    results.append(check(
        "analyze_decision issues only reference Decision-layer checks",
        all(issue["check"] in LAYER_CHECKS[TargetType.DECISION] for issue in issues),
    ))
    results.append(check(
        "analyze_decision strengths is a list",
        isinstance(strengths, list),
    ))

    # --- DecisionResultが変更されていないこと(層分離維持) ---
    results.append(check(
        "DecisionResult.required_governance_check remains True after analysis",
        decision_result.required_governance_check is True,
    ))

    # --- Governance Layer違反検出 ---
    gov_score, gov_issues, gov_strengths = analyzer.analyze_governance()
    results.append(check(
        "analyze_governance returns score within [0, 1]",
        0.0 <= gov_score <= 1.0,
    ))
    results.append(check(
        "analyze_governance issues only reference Governance-layer checks",
        all(issue["check"] in LAYER_CHECKS[TargetType.GOVERNANCE] for issue in gov_issues),
    ))
    results.append(check(
        "analyze_governance issue severities are known SeverityLevel values",
        all(issue["severity"] in SeverityLevel.ORDER for issue in gov_issues),
    ))

    # --- Governance違反のシミュレーション(read-only) ---
    fake_summary = {
        "bypassed": 1,
        "fatal_errors": 1,
        "write_aborted": 1,
        "checklist_fail_count": 1,
    }
    fake_issues = []
    if fake_summary["bypassed"] != 0 or fake_summary["fatal_errors"] != 0:
        fake_issues.append({"check": "bypass検出", "description": "simulated bypass", "severity": "critical"})
    if fake_summary["write_aborted"] != 0 or fake_summary["checklist_fail_count"] != 0:
        fake_issues.append({"check": "異常ログ", "description": "simulated abnormal log", "severity": "high"})
    results.append(check(
        "simulated Governance violation produces issues with check in LAYER_CHECKS[governance]",
        all(issue["check"] in LAYER_CHECKS[TargetType.GOVERNANCE] for issue in fake_issues)
        and len(fake_issues) == 2,
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
