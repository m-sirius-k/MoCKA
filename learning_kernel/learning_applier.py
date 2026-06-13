"""
MoCKA 3.0 — Self-Learning Kernel
learning_applier.py

責務:
  Learning Queueで status="approved" となったLearningUpdateのみを
  WeightStateStoreへ適用する。

  適用条件:
    - update.status == "approved"
    - governance_status == "PASS"
    - Update Validatorによる再検証(現在のstate/直近statusに基づく)がpassedであること

  いずれかを満たさない場合は適用せず、ValueErrorを発生させる
  (呼び出し側がGovernance/Queueの状態を誤って適用しないための安全策)。

  適用後、LearningQueue上のstatusは"applied"に更新される。
"""

from learning_model import LearningUpdate
from learning_queue import LearningQueue
from learning_registry import UpdateStatus
from update_validator import UpdateValidator
from weight_state_store import WeightStateStore


class LearningApplier:
    def __init__(self, validator: UpdateValidator = None):
        self._validator = validator or UpdateValidator()

    def apply(
        self,
        update: LearningUpdate,
        state_store: WeightStateStore,
        queue: LearningQueue,
        governance_status: str,
    ) -> LearningUpdate:
        if update.status != UpdateStatus.APPROVED:
            raise ValueError(
                f"update '{update.update_id}' is not approved (status={update.status})"
            )

        if governance_status != "PASS":
            raise ValueError(
                f"cannot apply update '{update.update_id}': governance_status='{governance_status}' != 'PASS'"
            )

        recheck = self._validator.validate(
            action=update.action,
            governance_status=governance_status,
            recent_statuses=queue.recent_statuses(),
        )
        if not recheck.passed:
            raise ValueError(
                f"cannot apply update '{update.update_id}': re-validation failed ({recheck.reasons})"
            )

        action = update.action
        state_store.apply_delta(action.parameter, action.delta)
        return queue.mark_applied(update.update_id)
