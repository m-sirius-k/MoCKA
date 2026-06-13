"""
MoCKA 3.0 — Self-Learning Kernel
learning_queue.py

責務:
  検証済みのLearningActionを「即時反映せず」キューに保管する。
  Learning Kernelにおける学習更新は、必ず本Queueを経由する
  (即時反映禁止の実装)。

  - 永続化先: learning_kernel/data/learning_queue.json
  - LearningUpdate.status: "pending" | "approved" | "rejected" | "applied" | "rolled_back"
  - enqueue時にValidationResult.passed=Falseであれば、status="rejected"として登録する
    (Update Validatorで不合格となったActionはQueueに積まれるが、適用対象にはならない)
"""

import json
from pathlib import Path
from typing import List, Optional, Sequence

from learning_model import LearningAction, LearningUpdate, ValidationResult
from learning_registry import UpdateStatus

_DATA_DIR = Path(__file__).resolve().parent / "data"
_QUEUE_FILE = _DATA_DIR / "learning_queue.json"


class LearningQueue:
    def __init__(self, queue_file: Optional[Path] = None):
        self._queue_file = queue_file or _QUEUE_FILE
        self._queue_file.parent.mkdir(parents=True, exist_ok=True)
        self._updates: List[LearningUpdate] = self._load()

    def _load(self) -> List[LearningUpdate]:
        if self._queue_file.exists():
            data = json.loads(self._queue_file.read_text(encoding="utf-8"))
            return [LearningUpdate.from_dict(d) for d in data.get("updates", [])]
        return []

    def _save(self):
        data = {"updates": [u.to_dict() for u in self._updates]}
        self._queue_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def enqueue(self, action: LearningAction, validation_result: ValidationResult) -> LearningUpdate:
        update_id = f"LU-{len(self._updates) + 1:04d}-{action.action_id}"
        status = UpdateStatus.PENDING if validation_result.passed else UpdateStatus.REJECTED
        update = LearningUpdate(
            update_id=update_id,
            action=action,
            status=status,
            validation_result=validation_result,
        )
        self._updates.append(update)
        self._save()
        return update

    def get(self, update_id: str) -> Optional[LearningUpdate]:
        for update in self._updates:
            if update.update_id == update_id:
                return update
        return None

    def _replace(self, update_id: str, new_update: LearningUpdate) -> LearningUpdate:
        for i, update in enumerate(self._updates):
            if update.update_id == update_id:
                self._updates[i] = new_update
                self._save()
                return new_update
        raise KeyError(f"unknown update_id: {update_id}")

    def approve(self, update_id: str) -> LearningUpdate:
        update = self.get(update_id)
        if update is None:
            raise KeyError(f"unknown update_id: {update_id}")
        if update.status != UpdateStatus.PENDING:
            raise ValueError(f"update '{update_id}' is not pending (status={update.status})")
        new_update = LearningUpdate(
            update_id=update.update_id,
            action=update.action,
            status=UpdateStatus.APPROVED,
            validation_result=update.validation_result,
        )
        return self._replace(update_id, new_update)

    def reject(self, update_id: str) -> LearningUpdate:
        update = self.get(update_id)
        if update is None:
            raise KeyError(f"unknown update_id: {update_id}")
        new_update = LearningUpdate(
            update_id=update.update_id,
            action=update.action,
            status=UpdateStatus.REJECTED,
            validation_result=update.validation_result,
        )
        return self._replace(update_id, new_update)

    def mark_applied(self, update_id: str) -> LearningUpdate:
        update = self.get(update_id)
        if update is None:
            raise KeyError(f"unknown update_id: {update_id}")
        if update.status != UpdateStatus.APPROVED:
            raise ValueError(f"update '{update_id}' is not approved (status={update.status})")
        new_update = LearningUpdate(
            update_id=update.update_id,
            action=update.action,
            status=UpdateStatus.APPLIED,
            validation_result=update.validation_result,
        )
        return self._replace(update_id, new_update)

    def mark_rolled_back(self, update_id: str) -> LearningUpdate:
        update = self.get(update_id)
        if update is None:
            raise KeyError(f"unknown update_id: {update_id}")
        if update.status != UpdateStatus.APPLIED:
            raise ValueError(f"update '{update_id}' is not applied (status={update.status})")
        new_update = LearningUpdate(
            update_id=update.update_id,
            action=update.action,
            status=UpdateStatus.ROLLED_BACK,
            validation_result=update.validation_result,
        )
        return self._replace(update_id, new_update)

    def list(self, status: Optional[str] = None) -> List[LearningUpdate]:
        if status is None:
            return list(self._updates)
        return [u for u in self._updates if u.status == status]

    def recent_statuses(self, limit: int = 10) -> Sequence[str]:
        return tuple(u.status for u in self._updates[-limit:])
