"""PHI-OS Core v1

Orchestra / Relay / Memory など全製品が共通で呼び出すコア。
セッション管理・ISE接続・Handshake共通処理を提供する最小実装。
"""
from __future__ import annotations

from ise.state_machine import ISEState, can_transition, transition
from ise.decision_ledger import append_decision
from ise.fluid_connector import notify_trajectory


class PHIOSCore:
    """全製品が共有するPHI-OSセッションコア"""

    def __init__(self):
        self.state = ISEState.INITIALIZING

    def start(self, actor: str, event_id: str) -> ISEState:
        """セッションを開始し、INITIALIZING → ACTIVE に遷移する"""
        return self._move_to(ISEState.ACTIVE, actor, event_id, reason="session_start")

    def degrade(self, actor: str, event_id: str, reason: str) -> ISEState:
        """異常検知時に ACTIVE → DEGRADED に遷移する"""
        return self._move_to(ISEState.DEGRADED, actor, event_id, reason=reason)

    def recover(self, actor: str, event_id: str) -> ISEState:
        """DEGRADED → ACTIVE に復帰する"""
        return self._move_to(ISEState.ACTIVE, actor, event_id, reason="recovered")

    def _move_to(self, next_state: ISEState, actor: str, event_id: str, reason: str) -> ISEState:
        before = self.state
        if not can_transition(before, next_state):
            raise ValueError(f"Invalid transition: {before} -> {next_state}")

        self.state = transition(before, next_state)

        append_decision(
            decision_type="state_transition",
            actor=actor,
            before=before.value,
            after=self.state.value,
            reason=reason,
        )
        notify_trajectory(before.value, self.state.value, event_id)
        return self.state
