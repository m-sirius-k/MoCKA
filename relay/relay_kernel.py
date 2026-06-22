# relay/relay_kernel.py
# Relay Kernel Phase1 — Relayをstateless bridgeからstateful kernelへ進化させる中核。
#
# 禁止事項(確定ルール):
#   - 判断しない（Policy Engineの領域を侵食しない）
#   - 検証しない（validateはevent_gate側の責務）
#   - 意味付けしない（reduceは機械的な状態遷移のみ）
# RelayKernelはDBへの永続化を行わない。プロセス内のstate/historyのみを保持する。
#
# Phase2: PolicyEngineはstateを読み取るだけで、stateそのものを変更しない。
# Phase3: ActionRouterはdecisionをactionへ写像するだけで、stateを変更しない。
# Phase4: QUEUE_EVENT判定されたイベントはEventQueueへ実体としてpushされる
#         (Phase3まではdefer判定時にイベントが単に破棄されていたギャップを解消)。
#         ReplayEngineはhistoryからのin-memory状態再構築を提供する。

from .policy_engine import PolicyEngine
from .action_router import ActionRouter
from .event_queue import EventQueue
from .replay_engine import ReplayEngine


class RelayKernel:
    def __init__(self):
        self.state = {}
        self.history = []
        self.policy = PolicyEngine()
        self.action_router = ActionRouter()
        self.queue = EventQueue()
        self.replay_engine = ReplayEngine(self)

    def ingest(self, event: dict) -> dict:
        self.history.append(event)
        self.state = self.reduce(event, self.state)
        decision = self.policy.evaluate(self.state)
        action = self.action_router.route(self.state, decision)

        if action["action"] == "QUEUE_EVENT":
            self.queue.push(event)

        return {
            "state": self.state,
            "policy": decision,
            "action": action,
        }

    def reduce(self, event: dict, state: dict) -> dict:
        return {
            "last_type": event.get("type"),
            "last_source": event.get("source"),
            "event_count": state.get("event_count", 0) + 1,
        }
