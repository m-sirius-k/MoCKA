# runtime/execution/runner.py
# MoCKA v1.2.1+ — Runner（統合起動制御）
# 責務: MoCKAシステムの実行を制御する。core層には触れない。

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from core.bridge.phi_personal_bridge import ConflictInput
from runtime.logging import RuntimeLogger

if TYPE_CHECKING:
    pass


class Runner:
    """
    MoCKA.run_cycle() のラッパー。
    - 実行回数のカウント
    - RuntimeLogger への記録
    - 将来の retry / timeout / rate-limit はここに集約する
    """

    def __init__(self, system: Any) -> None:
        self.system  = system
        self._count  = 0
        self._logger = RuntimeLogger()

    def run(self, event: ConflictInput) -> Dict[str, Any]:
        """1サイクルを実行し、ログを記録して結果を返す。"""
        self._count += 1
        cycle_id = f"{self._count:03d}"

        result = self.system._internal_cycle(event)

        self._logger.log_cycle(cycle_id, result)

        return result

    @property
    def cycle_count(self) -> int:
        return self._count
