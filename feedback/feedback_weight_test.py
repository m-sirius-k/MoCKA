"""
MoCKA 3.0 — Feedback Loop Weight調整テスト

確認内容:
  - WeightOptimizerがDecision/Memory/Semanticの重み調整案を生成すること
  - 調整案にmodule/parameter/suggested_delta/direction/reasonが含まれること
  - severityが高いほどsuggested_deltaの絶対値が大きいこと
  - DecisionTuner/MemoryReinforcer/SemanticAdjusterが
    対応するtuning_type/reinforcement_type/adjustment_typeを返すこと
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SELF_AUDIT_DIR = _HERE.parent / "self_audit"

for _dir in (_HERE, _SELF_AUDIT_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from audit_model import Issue  # noqa: E402

from decision_tuner import DecisionTuner  # noqa: E402
from memory_reinforcer import MemoryReinforcer  # noqa: E402
from semantic_adjuster import SemanticAdjuster  # noqa: E402
from weight_optimizer import WeightOptimizer  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    optimizer = WeightOptimizer()
    tuner = DecisionTuner()
    reinforcer = MemoryReinforcer()
    adjuster = SemanticAdjuster()

    required_keys = {"module", "parameter", "current_weight", "suggested_delta", "direction", "reason"}

    # --- Decision Layer ---
    priority_issue_low = Issue("priority妥当性", "priority issue", "low")
    priority_issue_critical = Issue("priority妥当性", "priority issue", "critical")
    risk_issue = Issue("risk整合性", "risk issue", "high")

    priority_adj_low = optimizer.decision_weight_adjustment(priority_issue_low)
    priority_adj_critical = optimizer.decision_weight_adjustment(priority_issue_critical)
    risk_adj = optimizer.decision_weight_adjustment(risk_issue)

    results.append(check(
        "decision_weight_adjustment(priority妥当性) contains required keys",
        required_keys <= set(priority_adj_low.keys()),
    ))
    results.append(check(
        "decision_weight_adjustment(risk整合性) targets risk_analyzer.py",
        risk_adj["module"] == "decision/risk_analyzer.py",
    ))
    results.append(check(
        "higher severity yields a larger |suggested_delta| (priority妥当性)",
        abs(priority_adj_critical["suggested_delta"]) > abs(priority_adj_low["suggested_delta"]),
    ))

    # --- Memory Layer ---
    reuse_issue = Issue("再利用性", "reuse issue", "medium")
    noise_issue = Issue("ノイズ率", "noise issue", "high")

    reuse_adj = optimizer.memory_weight_adjustment(reuse_issue)
    noise_adj = optimizer.memory_weight_adjustment(noise_issue)

    results.append(check(
        "memory_weight_adjustment(再利用性) contains required keys",
        required_keys <= set(reuse_adj.keys()),
    ))
    results.append(check(
        "memory_weight_adjustment(再利用性) increases intent_match",
        reuse_adj["parameter"] == "intent_match" and reuse_adj["direction"] == "increase",
    ))
    results.append(check(
        "memory_weight_adjustment(ノイズ率) decreases recency_decay",
        noise_adj["parameter"] == "recency_decay" and noise_adj["direction"] == "decrease",
    ))

    # --- Semantic Layer ---
    intent_issue = Issue("意図分類精度", "intent accuracy issue", "medium")
    semantic_adj = optimizer.semantic_threshold_adjustment(intent_issue)
    results.append(check(
        "semantic_threshold_adjustment(意図分類精度) contains required keys",
        required_keys <= set(semantic_adj.keys()),
    ))
    results.append(check(
        "semantic_threshold_adjustment(意図分類精度) targets confidence_threshold",
        semantic_adj["parameter"] == "confidence_threshold",
    ))

    # --- 未対応checkの場合は調整なし ---
    unknown_issue = Issue("未定義チェック", "unknown", "low")
    unknown_adj = optimizer.decision_weight_adjustment(unknown_issue)
    results.append(check(
        "unsupported check yields suggested_delta == 0.0 (direction='none')",
        unknown_adj["suggested_delta"] == 0.0 and unknown_adj["direction"] == "none",
    ))

    # --- DecisionTuner ---
    rationale_issue = Issue("rationale一貫性", "rationale issue", "low")
    risk_tuning = tuner.propose(risk_issue)
    priority_tuning = tuner.propose(priority_issue_low)
    rationale_tuning = tuner.propose(rationale_issue)

    results.append(check(
        "DecisionTuner.propose(risk整合性) == risk_scoring_correction",
        risk_tuning["tuning_type"] == "risk_scoring_correction",
    ))
    results.append(check(
        "DecisionTuner.propose(priority妥当性) == priority_scoring_redistribution",
        priority_tuning["tuning_type"] == "priority_scoring_redistribution",
    ))
    results.append(check(
        "DecisionTuner.propose(rationale一貫性) == rationale_structure_improvement",
        rationale_tuning["tuning_type"] == "rationale_structure_improvement",
    ))

    # --- MemoryReinforcer ---
    consistency_issue = Issue("一貫性", "consistency issue", "medium")
    reinforcement = reinforcer.propose(consistency_issue)
    decay = reinforcer.propose(noise_issue)
    reuse_reinforcement = reinforcer.propose(reuse_issue)

    results.append(check(
        "MemoryReinforcer.propose(一貫性) == reinforce_success_patterns",
        reinforcement["reinforcement_type"] == "reinforce_success_patterns",
    ))
    results.append(check(
        "MemoryReinforcer.propose(ノイズ率) == decay_low_value_memories",
        decay["reinforcement_type"] == "decay_low_value_memories",
    ))
    results.append(check(
        "MemoryReinforcer.propose(再利用性) == adjust_reuse_frequency",
        reuse_reinforcement["reinforcement_type"] == "adjust_reuse_frequency",
    ))
    results.append(check(
        "decay_low_value_memories description does not propose deletion",
        "削除" not in decay["description"] or "削除は提案しない" in decay["description"],
    ))

    # --- SemanticAdjuster ---
    intent_adjustment = adjuster.propose(intent_issue)
    context_issue = Issue("context補完妥当性", "context issue", "low")
    context_adjustment = adjuster.propose(context_issue)

    results.append(check(
        "SemanticAdjuster.propose(意図分類精度) == intent_classification_improvement",
        intent_adjustment["adjustment_type"] == "intent_classification_improvement",
    ))
    results.append(check(
        "SemanticAdjuster.propose(context補完妥当性) == context_completion_improvement",
        context_adjustment["adjustment_type"] == "context_completion_improvement",
    ))
    results.append(check(
        "intent_classification_improvement marks registry_candidate=True",
        intent_adjustment["registry_candidate"] is True,
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
