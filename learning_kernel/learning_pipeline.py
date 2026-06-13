"""
MoCKA 3.0 — Self-Learning Kernel
learning_pipeline.py

責務:
  Self-Learning Kernelのエントリーポイント。Feedback Loop(Phase 3-2)から
  Learning State更新までの三段階適用構造を実行する。

  Update Flow:
    FeedbackProposal
       |
       v
    Learning Engine        (feedback -> LearningAction)
       |
       v
    Update Validator        (安全性検証)
       |
       v
    Learning Queue          (pending / rejected として保管。即時反映なし)
       |
       v
    Governance Check         (approve_and_apply時に再確認)
       |
       v
    Learning Applier         (approved のみ WeightStateStore へ適用)
       |
       v
    Updated Learning State

  run()は Feedback生成 -> LearningAction変換 -> 検証 -> Queue登録 までを行い、
  Queue登録時点では一切のLearning Stateを変更しない(自動適用禁止)。

  承認・適用・rollbackは別メソッド(approve_and_apply / rollback)として
  明示的に呼び出す必要があり、run()からは行われない。
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FEEDBACK_DIR = _HERE.parent / "feedback"
_SELF_AUDIT_DIR = _HERE.parent / "self_audit"

for _dir in (_HERE, _FEEDBACK_DIR, _SELF_AUDIT_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from feedback_pipeline import FeedbackPipeline  # noqa: E402

from learning_applier import LearningApplier  # noqa: E402
from learning_engine import LearningEngine  # noqa: E402
from learning_model import LearningUpdate  # noqa: E402
from learning_queue import LearningQueue  # noqa: E402
from update_validator import UpdateValidator  # noqa: E402
from weight_state_store import WeightStateStore  # noqa: E402


class LearningPipeline:
    def __init__(
        self,
        state_store: WeightStateStore = None,
        queue: LearningQueue = None,
        engine: LearningEngine = None,
        validator: UpdateValidator = None,
        applier: LearningApplier = None,
    ):
        self.state_store = state_store or WeightStateStore()
        self.queue = queue or LearningQueue()
        self.engine = engine or LearningEngine()
        self.validator = validator or UpdateValidator()
        self.applier = applier or LearningApplier(validator=self.validator)

    def run(self):
        """
        FeedbackPipelineを実行し、生成されたFeedbackProposalを
        LearningActionへ変換、Update Validatorで検証してQueueへ
        登録する。Queue登録のみであり、Learning Stateは変更しない。

        戻り値: (FeedbackBatch, tuple[LearningUpdate, ...])
        """
        batch = FeedbackPipeline().run()
        governance_status = batch.governance_status

        updates = []
        for proposal in batch.proposals:
            action = self.engine.convert(proposal, state_store=self.state_store)
            if action is None:
                continue
            validation_result = self.validator.validate(
                action=action,
                governance_status=governance_status,
                recent_statuses=self.queue.recent_statuses(),
            )
            update = self.queue.enqueue(action, validation_result)
            updates.append(update)

        return batch, tuple(updates)

    def approve_and_apply(self, update_id: str, governance_status: str) -> LearningUpdate:
        """
        Queue内のpending Updateを承認し、その場でApplierに適用させる。
        governance_status='PASS'でない場合は適用されず例外となる。
        """
        self.queue.approve(update_id)
        update = self.queue.get(update_id)
        return self.applier.apply(
            update=update,
            state_store=self.state_store,
            queue=self.queue,
            governance_status=governance_status,
        )

    def rollback(self, steps: int = 1):
        """
        WeightStateStoreをstep数分ロールバックする。
        Queue上のLearningUpdate(直近のapplied)をrolled_backとして記録する。
        """
        applied = self.queue.list(status="applied")
        for update in applied[-steps:][::-1]:
            self.queue.mark_rolled_back(update.update_id)
        return self.state_store.rollback(steps=steps)


if __name__ == "__main__":
    pipeline = LearningPipeline()
    feedback_batch, learning_updates = pipeline.run()
    print(f"feedback proposals: {len(feedback_batch.proposals)}")
    print(f"learning updates queued: {len(learning_updates)}")
    for u in learning_updates:
        print(f"  {u.update_id}: status={u.status} parameter={u.action.parameter} delta={u.action.delta}")
