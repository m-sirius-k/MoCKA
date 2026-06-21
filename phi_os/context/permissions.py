"""
H2-1 権限モデル(確定) — observe / write / control の定義と付与制約。
参照: H2_PARTIAL_SPEC_v1.0 第2節。H2-3(Trustの発火条件)はここに実装しない。
"""
from __future__ import annotations

OBSERVE = "observe"
WRITE = "write"
CONTROL = "control"

GLOBAL = "global"
ACTOR_SCOPED = "actor-scoped"

HAB_ACTOR_ID = "HAB"


class PermissionError(Exception):
    pass


def check_observe(requesting_actor_id: str, target_actor_id: str | None, scope: str) -> bool:
    """observe権限チェック。scopeが'global'なら誰でも観測可能。
    'actor-scoped'なら自身のactor_idのみ観測可能(2.2/3.2/3.3)。"""
    if scope == GLOBAL:
        return True
    if scope == ACTOR_SCOPED:
        return bool(requesting_actor_id) and requesting_actor_id == target_actor_id
    raise PermissionError(f"未知のobserve scope: {scope}")


def check_write(actor_id: str, target_actor_id: str) -> bool:
    """write権限チェック。自身のactor_idに紐づく状態のみ変更可能(2.2)。"""
    return bool(actor_id) and actor_id == target_actor_id


def check_control(actor_id: str) -> bool:
    """control権限チェック。HAB専属(2.2)。外部AIへの付与は一切禁止。"""
    return actor_id == HAB_ACTOR_ID
