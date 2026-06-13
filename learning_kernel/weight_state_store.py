"""
MoCKA 3.0 — Self-Learning Kernel
weight_state_store.py

責務:
  LearningStateのJSON永続化と、apply_delta/rollbackによる
  安全な状態更新を担う。

  - 永続化先: learning_kernel/data/learning_state.json
  - {"state": {...LearningState.to_dict()...}, "history": [前バージョンのstate, ...]}
  - apply_deltaはPARAM_BOUNDSによるクリッピングを行う
  - rollbackはhistoryから直前の状態を復元する
"""

import json
from pathlib import Path
from typing import Optional

from learning_registry import get_param_bounds
from learning_state import LearningState, get_value, with_value

_DATA_DIR = Path(__file__).resolve().parent / "data"
_STATE_FILE = _DATA_DIR / "learning_state.json"


class WeightStateStore:
    def __init__(self, state_file: Optional[Path] = None):
        self._state_file = state_file or _STATE_FILE
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state, self._history = self._load()

    def _load(self):
        if self._state_file.exists():
            data = json.loads(self._state_file.read_text(encoding="utf-8"))
            state = LearningState.from_dict(data["state"])
            history = [LearningState.from_dict(h) for h in data.get("history", [])]
            return state, history
        return LearningState.default(), []

    def _save(self):
        data = {
            "state": self._state.to_dict(),
            "history": [h.to_dict() for h in self._history],
        }
        self._state_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def current(self) -> LearningState:
        return self._state

    def get_value(self, path: str):
        return get_value(self._state, path)

    def apply_delta(self, path: str, delta: float) -> LearningState:
        """
        path(dotパス)の値にdeltaを加算した新しいLearningStateを保存する。
        PARAM_BOUNDSが定義されている場合、結果値はその範囲にクリップされる。
        直前のstateはhistoryに退避され、rollback可能性を保つ。
        """
        current_value = get_value(self._state, path)
        new_value = current_value + delta

        bounds = get_param_bounds(path)
        if bounds is not None:
            lower, upper = bounds
            new_value = max(lower, min(upper, new_value))

        self._history.append(self._state)
        self._state = with_value(self._state, path, new_value)
        self._save()
        return self._state

    def rollback(self, steps: int = 1) -> LearningState:
        """
        historyから直前(または指定step数前)のLearningStateへ復元する。
        historyが不足している場合は可能な範囲のみ戻す。
        """
        for _ in range(steps):
            if not self._history:
                break
            self._state = self._history.pop()
        self._save()
        return self._state

    def history_length(self) -> int:
        return len(self._history)
