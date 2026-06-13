"""
MoCKA 3.0 — Self-Learning Kernel 統合テスト

確認内容:
  - Feedback -> Learning変換が成功すること(LearningEngine.convert)
  - 検証(UpdateValidator)を通過したActionがQueueにpendingとして登録されること
  - approve_and_apply によりWeight State(LearningState)が更新されること
  - LearningPipeline.run() がFeedbackPipelineを実行しQueueへ反映すること
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

from learning_engine import LearningEngine  # noqa: E402
from learning_pipeline import LearningPipeline  # noqa: E402
from learning_queue import LearningQueue  # noqa: E402
from update_validator import UpdateValidator  # noqa: E402
from weight_state_store import WeightStateStore  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def _make_proposal(parameter, suggested_delta, direction, target_layer="decision"):
    return FeedbackProposal(
        feedback_id=f"FB-TEST-{parameter}-{direction}",
        source_audit_id="AUDIT-TEST",
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
        state_file = Path(tmpdir) / "learning_state.json"
        queue_file = Path(tmpdir) / "learning_queue.json"

        store = WeightStateStore(state_file=state_file)
        queue = LearningQueue(queue_file=queue_file)
        engine = LearningEngine()
        validator = UpdateValidator()

        # --- Feedback -> Learning変換成功 ---
        proposal = _make_proposal("intent_clarity", 0.05, "increase")
        action = engine.convert(proposal, state_store=store)
        results.append(check("LearningEngine.convert returns a LearningAction", action is not None))
        results.append(check(
            "converted action targets decision.priority_weights.intent_clarity",
            action.parameter == "decision.priority_weights.intent_clarity",
        ))
        results.append(check(
            "converted action delta has correct sign (increase -> positive)",
            action.delta == 0.05,
        ))

        # --- 未対応parameterはNone ---
        unsupported = _make_proposal("unknown", 0.0, "none")
        results.append(check(
            "unsupported parameter/direction yields no LearningAction",
            engine.convert(unsupported, state_store=store) is None,
        ))

        # --- Validator通過 ---
        vr = validator.validate(action, governance_status="PASS", recent_statuses=())
        results.append(check("UpdateValidator.validate passes for a valid small-delta action", vr.passed))

        # --- Queue保管 ---
        update = queue.enqueue(action, vr)
        results.append(check("enqueue stores update with status='pending'", update.status == "pending"))
        results.append(check("queue.list(pending) contains the new update", update in queue.list(status="pending")))

        # --- Governance承認フロー & Kernel Update ---
        before_value = store.get_value(action.parameter)
        pipeline = LearningPipeline(state_store=store, queue=queue, engine=engine, validator=validator)
        applied = pipeline.approve_and_apply(update.update_id, governance_status="PASS")
        after_value = store.get_value(action.parameter)

        results.append(check("approve_and_apply marks update as 'applied'", applied.status == "applied"))
        results.append(check(
            "Learning State value increased by delta after apply",
            abs(after_value - before_value - action.delta) < 1e-9,
        ))

        # --- LearningPipeline.run() ---
        store2 = WeightStateStore(state_file=Path(tmpdir) / "learning_state_2.json")
        queue2 = LearningQueue(queue_file=Path(tmpdir) / "learning_queue_2.json")
        pipeline2 = LearningPipeline(state_store=store2, queue=queue2)
        batch, updates = pipeline2.run()
        results.append(check("LearningPipeline.run() returns a FeedbackBatch", batch is not None))
        results.append(check("LearningPipeline.run() returns a tuple of LearningUpdate", isinstance(updates, tuple)))
        results.append(check(
            "LearningPipeline.run() does not modify Learning State (no auto-apply)",
            store2.current().version == 1,
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
