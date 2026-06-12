"""ISE State Machine v1"""
from enum import Enum


class ISEState(Enum):
    INITIALIZING = "initializing"
    ACTIVE       = "active"
    DEGRADED     = "degraded"
    SUSPENDED    = "suspended"
    SEALED       = "sealed"


# 許可される遷移 {from: [to, ...]}
TRANSITIONS = {
    ISEState.INITIALIZING: [ISEState.ACTIVE],
    ISEState.ACTIVE:       [ISEState.DEGRADED, ISEState.SUSPENDED, ISEState.SEALED],
    ISEState.DEGRADED:     [ISEState.ACTIVE, ISEState.SUSPENDED],
    ISEState.SUSPENDED:    [ISEState.ACTIVE],
    ISEState.SEALED:       [],  # 終端状態
}


def can_transition(current: ISEState, next_state: ISEState) -> bool:
    return next_state in TRANSITIONS.get(current, [])


def transition(current: ISEState, next_state: ISEState) -> ISEState:
    if not can_transition(current, next_state):
        raise ValueError(f"Invalid transition: {current} -> {next_state}")
    return next_state
