"""ISE Data Lifecycle Manager v1"""
from __future__ import annotations
from enum import Enum

from .snapshot_manager import SNAPSHOT_MAX_GENERATIONS
from .state_machine import ISEState


class LifecycleStage(Enum):
    RAW      = "raw"
    ACTIVE   = "active"
    SNAPSHOT = "snapshot"
    ARCHIVED = "archived"
    PURGED   = "purged"


def classify_snapshot(generation_index: int, ise_state: ISEState) -> LifecycleStage:
    """
    スナップショットのライフサイクル段階を判定する。

    generation_index: 新しい順に0始まりの世代インデックス
                       (0 = 最新スナップショット)
    ise_state:         そのスナップショットが属するISEの状態
    """
    if ise_state == ISEState.SEALED:
        return LifecycleStage.ARCHIVED
    if generation_index < SNAPSHOT_MAX_GENERATIONS:
        return LifecycleStage.SNAPSHOT
    if generation_index < SNAPSHOT_MAX_GENERATIONS * 2:
        return LifecycleStage.SNAPSHOT
    return LifecycleStage.PURGED


def is_purge_eligible(generation_index: int, ise_state: ISEState) -> bool:
    """保持期間を超過し削除対象となるかどうかを判定する"""
    return classify_snapshot(generation_index, ise_state) == LifecycleStage.PURGED
