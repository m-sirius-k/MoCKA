"""
MoCKA 3.0 — Decision Layer 統合テスト

確認内容:
  - SemanticResult -> DecisionResult変換
  - Priority整合性 (0-1範囲、action_profileに応じた相対関係)
  - Riskスコア生成 (0-1範囲、write_heavyがread_heavyより高リスク)
  - 複数候補処理 (alternativesが生成されること)
  - Governanceフラグ付与 (required_governance_check=True)
"""

import sys
from pathlib import Path

_SEMANTIC_DIR = Path(__file__).resolve().parent.parent / "semantic"
if str(_SEMANTIC_DIR) not in sys.path:
    sys.path.insert(0, str(_SEMANTIC_DIR))

from decision_pipeline import DecisionPipeline
from decision_registry import get_decision_profile
from decision_sample_cases import DECISION_SAMPLE_CASES


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []
    pipeline = DecisionPipeline()

    decision_results = {}

    for case in DECISION_SAMPLE_CASES:
        result = pipeline.process(case["text"], case["context"])
        decision_results[case["name"]] = result

        # SemanticResult -> DecisionResult 変換が行われていること
        results.append(check(
            f"DecisionResult.selected_action is non-empty: {case['name']}",
            bool(result.selected_action),
        ))

        # Priority/Risk整合性
        results.append(check(
            f"priority_score in [0,1]: {case['name']}",
            0.0 <= result.priority_score <= 1.0,
        ))
        results.append(check(
            f"risk_score in [0,1]: {case['name']}",
            0.0 <= result.risk_score <= 1.0,
        ))
        results.append(check(
            f"confidence in [0,1]: {case['name']}",
            0.0 <= result.confidence <= 1.0,
        ))

        # Governanceフラグ付与
        results.append(check(
            f"required_governance_check is True: {case['name']}",
            result.required_governance_check is True,
        ))

        # rationale / risk_factors / to_dict
        results.append(check(
            f"rationale is non-empty: {case['name']}",
            bool(result.rationale),
        ))
        results.append(check(
            f"to_dict() round-trips: {case['name']}",
            isinstance(result.to_dict(), dict) and "selected_action" in result.to_dict(),
        ))

    # --- 複数候補処理: alternativesが少なくとも1件生成されること ---
    for name, result in decision_results.items():
        results.append(check(
            f"alternatives is non-empty: {name}",
            len(result.alternatives) >= 1,
        ))

    # --- action_profileに応じた相対関係: write_heavyはread_heavyよりrisk_scoreが高い ---
    read_heavy_risk = decision_results["information_retrieval_read_heavy"].risk_score
    write_heavy_risk = decision_results["implementation_write_heavy"].risk_score
    results.append(check(
        "write_heavy risk_score > read_heavy risk_score",
        write_heavy_risk > read_heavy_risk,
    ))

    # --- unknown intentのfallback profileが適用されること ---
    unknown_profile = get_decision_profile("unknown")
    results.append(check(
        "unknown intent maps to verification_first fallback profile",
        unknown_profile.action_profile == "verification_first",
    ))
    unknown_result = decision_results["unknown_intent_fallback"]
    results.append(check(
        "unknown intent decision has elevated risk_score (> 0.3)",
        unknown_result.risk_score > 0.3,
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
