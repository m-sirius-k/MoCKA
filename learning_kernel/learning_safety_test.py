"""
MoCKA 3.0 — Self-Learning Kernel 安全性テスト

確認内容:
  - Governance未承認(governance_status != 'PASS')では検証・適用が拒否されること
  - MAX_DELTAを超えるdeltaは拒否されること
  - risk_weights系パラメータでRISK_INCREASE_LIMITを超える増加は拒否されること
  - PARAM_BOUNDS外となる更新は拒否されること
  - stability_scoreが閾値未満の場合は拒否されること
  - status="rejected"のUpdateはapprove/applyできないこと
  - approve済みでもgovernance_status!='PASS'ならApplierが適用しないこと
  - rollback機構が正しく動作すること(値の復元 + status='rolled_back')
"""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FEEDBACK_DIR = _HERE.parent / "feedback"
for _dir in (_HERE, _FEEDBACK_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from feedback_model import FeedbackProposal  # noqa: E402

from learning_applier import LearningApplier  # noqa: E402
from learning_engine import LearningEngine  # noqa: E402
from learning_model import LearningAction  # noqa: E402
from learning_pipeline import LearningPipeline  # noqa: E402
from learning_queue import LearningQueue  # noqa: E402
from learning_registry import MAX_DELTA, RISK_INCREASE_LIMIT, STABILITY_THRESHOLD  # noqa: E402
from update_validator import UpdateValidator  # noqa: E402
from weight_state_store import WeightStateStore  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def _make_proposal(parameter, suggested_delta, direction, target_layer="decision", feedback_id=None):
    return FeedbackProposal(
        feedback_id=feedback_id or f"FB-SAFETY-{parameter}-{direction}",
        source_audit_id="AUDIT-SAFETY",
        target_layer=target_layer,
        issue_reference="test_issue",
        suggested_change={
            "weight_adjustment": {
                "module": target_layer,
                "parameter": parameter,
                "current_weight": None,
                "suggested_delta": suggested_delta,
                "direction": direction,
                "reason": "test reason",
            }
        },
        expected_impact=0.5,
        confidence=0.8,
        risk_level="medium",
    )


def main():
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        store = WeightStateStore(state_file=Path(tmpdir) / "state.json")
        queue = LearningQueue(queue_file=Path(tmpdir) / "queue.json")
        engine = LearningEngine()
        validator = UpdateValidator()
        applier = LearningApplier(validator=validator)

        valid_proposal = _make_proposal("intent_clarity", 0.05, "increase")
        valid_action = engine.convert(valid_proposal, state_store=store)

        # --- Governance未承認時は検証拒否 ---
        vr_fail_gov = validator.validate(valid_action, governance_status="FAIL", recent_statuses=())
        results.append(check(
            "validation fails when governance_status != 'PASS'",
            not vr_fail_gov.passed and vr_fail_gov.checks["governance_compliance"] is False,
        ))

        # --- MAX_DELTA超過は拒否 ---
        big_delta_action = LearningAction(
            action_id="LA-BIG",
            source_feedback_id="FB-BIG",
            target_layer="decision",
            parameter="decision.priority_weights.intent_clarity",
            delta=MAX_DELTA + 0.05,
            current_value=store.get_value("decision.priority_weights.intent_clarity"),
            proposed_value=store.get_value("decision.priority_weights.intent_clarity") + MAX_DELTA + 0.05,
            priority="high",
            rationale="too big",
        )
        vr_big = validator.validate(big_delta_action, governance_status="PASS", recent_statuses=())
        results.append(check(
            "validation rejects |delta| > MAX_DELTA",
            not vr_big.passed and vr_big.checks["max_delta"] is False,
        ))

        # --- risk_weights増加でRISK_INCREASE_LIMIT超過は拒否 ---
        risk_action = LearningAction(
            action_id="LA-RISK",
            source_feedback_id="FB-RISK",
            target_layer="decision",
            parameter="decision.risk_weights.governance_violation",
            delta=RISK_INCREASE_LIMIT + 0.02,
            current_value=store.get_value("decision.risk_weights.governance_violation"),
            proposed_value=store.get_value("decision.risk_weights.governance_violation") + RISK_INCREASE_LIMIT + 0.02,
            priority="high",
            rationale="risk increase too large",
        )
        vr_risk = validator.validate(risk_action, governance_status="PASS", recent_statuses=())
        results.append(check(
            "validation rejects risk_weights increase > RISK_INCREASE_LIMIT",
            not vr_risk.passed and vr_risk.checks["risk_increase"] is False,
        ))

        # --- PARAM_BOUNDS外は拒否 ---
        out_of_bounds_action = LearningAction(
            action_id="LA-OOB",
            source_feedback_id="FB-OOB",
            target_layer="decision",
            parameter="decision.priority_weights.intent_clarity",
            delta=0.05,
            current_value=0.97,
            proposed_value=1.02,
            priority="medium",
            rationale="out of bounds",
        )
        vr_oob = validator.validate(out_of_bounds_action, governance_status="PASS", recent_statuses=())
        results.append(check(
            "validation rejects proposed_value outside PARAM_BOUNDS",
            not vr_oob.passed and vr_oob.checks["bounds"] is False,
        ))

        # --- stability_score不足は拒否 ---
        unstable_history = tuple(["applied"] * 10)
        vr_unstable = validator.validate(valid_action, governance_status="PASS", recent_statuses=unstable_history)
        results.append(check(
            "validation rejects when stability_score < STABILITY_THRESHOLD",
            not vr_unstable.passed and vr_unstable.checks["stability"] is False,
        ))
        results.append(check(
            "stability_score below threshold is consistent with STABILITY_THRESHOLD constant",
            UpdateValidator.stability_score(unstable_history) < STABILITY_THRESHOLD,
        ))

        # --- rejectedはapprove不可 ---
        rejected_update = queue.enqueue(big_delta_action, vr_big)
        results.append(check("enqueue with failed validation results in status='rejected'", rejected_update.status == "rejected"))
        approve_failed = False
        try:
            queue.approve(rejected_update.update_id)
        except ValueError:
            approve_failed = True
        results.append(check("approve() raises ValueError for a rejected update", approve_failed))

        # --- approve済みでもgovernance未承認ならApplierが拒否 ---
        good_update = queue.enqueue(valid_action, validator.validate(valid_action, governance_status="PASS", recent_statuses=()))
        queue.approve(good_update.update_id)
        approved_update = queue.get(good_update.update_id)

        apply_blocked = False
        try:
            applier.apply(approved_update, store, queue, governance_status="FAIL")
        except ValueError:
            apply_blocked = True
        results.append(check(
            "LearningApplier.apply raises ValueError when governance_status != 'PASS'",
            apply_blocked,
        ))
        results.append(check(
            "Learning State is unchanged after a blocked apply",
            store.current().version == 1,
        ))

        # --- rollback機構 ---
        pipeline = LearningPipeline(state_store=store, queue=queue, engine=engine, validator=validator, applier=applier)
        before_value = store.get_value(valid_action.parameter)
        applied = applier.apply(approved_update, store, queue, governance_status="PASS")
        after_apply_value = store.get_value(valid_action.parameter)

        results.append(check("apply succeeds when governance_status == 'PASS'", applied.status == "applied"))
        results.append(check("apply changes the Learning State value", after_apply_value != before_value))

        restored_state = pipeline.rollback(steps=1)
        after_rollback_value = restored_state.to_dict()["decision"]["priority_weights"]["intent_clarity"]

        results.append(check(
            "rollback restores the previous Learning State value",
            abs(after_rollback_value - before_value) < 1e-9,
        ))
        rolled_back_update = queue.get(good_update.update_id)
        results.append(check(
            "rollback marks the corresponding update as 'rolled_back'",
            rolled_back_update.status == "rolled_back",
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
