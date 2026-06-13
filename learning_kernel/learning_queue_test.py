"""
MoCKA 3.0 — Self-Learning Kernel Queueテスト

確認内容:
  - enqueueされたLearningUpdateがJSONとして永続化され、再読込できること
  - update_id/target_layer/delta_values/priority/statusの構造が保持されること
  - approve/reject/mark_applied/mark_rolled_backの状態遷移が正しいこと
  - 不正な状態遷移(pending以外をapprove等)がエラーになること
  - recent_statusesが直近の状態を正しい順序で返すこと
"""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from learning_model import LearningAction, ValidationResult  # noqa: E402
from learning_queue import LearningQueue  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def _action(suffix, parameter="decision.priority_weights.intent_clarity", delta=0.02):
    return LearningAction(
        action_id=f"LA-{suffix}",
        source_feedback_id=f"FB-{suffix}",
        target_layer="decision",
        parameter=parameter,
        delta=delta,
        current_value=0.20,
        proposed_value=0.20 + delta,
        priority="medium",
        rationale="test",
    )


def _vr(passed=True):
    return ValidationResult(passed=passed, checks={"dummy": passed}, reasons=() if passed else ("dummy failed",))


def main():
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        queue_file = Path(tmpdir) / "queue.json"
        queue = LearningQueue(queue_file=queue_file)

        # --- enqueue: pending ---
        u1 = queue.enqueue(_action("1"), _vr(passed=True))
        results.append(check("enqueue with passed validation -> status='pending'", u1.status == "pending"))
        results.append(check("update has update_id", isinstance(u1.update_id, str) and len(u1.update_id) > 0))
        results.append(check("update.action.target_layer == 'decision'", u1.action.target_layer == "decision"))
        results.append(check("update.action.delta is preserved", u1.action.delta == 0.02))
        results.append(check("update.action.priority == 'medium'", u1.action.priority == "medium"))

        # --- enqueue: rejected ---
        u2 = queue.enqueue(_action("2"), _vr(passed=False))
        results.append(check("enqueue with failed validation -> status='rejected'", u2.status == "rejected"))

        # --- 永続化 & 再読込 ---
        queue_reloaded = LearningQueue(queue_file=queue_file)
        results.append(check("reloaded queue has the same number of updates", len(queue_reloaded.list()) == 2))
        reloaded_u1 = queue_reloaded.get(u1.update_id)
        results.append(check("reloaded update preserves status", reloaded_u1.status == "pending"))
        results.append(check("reloaded update preserves action.parameter", reloaded_u1.action.parameter == u1.action.parameter))

        # --- approve / mark_applied ---
        approved = queue_reloaded.approve(u1.update_id)
        results.append(check("approve() sets status='approved'", approved.status == "approved"))
        applied = queue_reloaded.mark_applied(u1.update_id)
        results.append(check("mark_applied() sets status='applied'", applied.status == "applied"))

        # --- 不正な状態遷移 ---
        approve_applied_failed = False
        try:
            queue_reloaded.approve(u1.update_id)
        except ValueError:
            approve_applied_failed = True
        results.append(check("approve() on an already-applied update raises ValueError", approve_applied_failed))

        mark_applied_pending_failed = False
        try:
            queue_reloaded.mark_applied(u2.update_id)
        except ValueError:
            mark_applied_pending_failed = True
        results.append(check("mark_applied() on a non-approved update raises ValueError", mark_applied_pending_failed))

        # --- reject ---
        u3 = queue_reloaded.enqueue(_action("3"), _vr(passed=True))
        rejected = queue_reloaded.reject(u3.update_id)
        results.append(check("reject() sets status='rejected'", rejected.status == "rejected"))

        # --- rollback ---
        rolled_back = queue_reloaded.mark_rolled_back(u1.update_id)
        results.append(check("mark_rolled_back() sets status='rolled_back'", rolled_back.status == "rolled_back"))
        rollback_pending_failed = False
        try:
            queue_reloaded.mark_rolled_back(u2.update_id)
        except ValueError:
            rollback_pending_failed = True
        results.append(check("mark_rolled_back() on a non-applied update raises ValueError", rollback_pending_failed))

        # --- recent_statuses ---
        all_statuses = [u.status for u in queue_reloaded.list()]
        results.append(check(
            "recent_statuses(limit) matches the tail of the full status list",
            list(queue_reloaded.recent_statuses(limit=2)) == all_statuses[-2:],
        ))

        # --- list(status=...) フィルタ ---
        rejected_updates = queue_reloaded.list(status="rejected")
        results.append(check(
            "list(status='rejected') returns only rejected updates",
            all(u.status == "rejected" for u in rejected_updates) and len(rejected_updates) >= 2,
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
