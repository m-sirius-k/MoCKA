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
# Phase5 Step3-1: EventRepositoryをappend-onlyのhookとして接続する。
#         ingestの契約({state, policy, action})・既存処理(history/reduce/policy/action_router)は
#         一切変更しない。EventRepositoryへの書き込みはhistory.appendの副作用として追加するのみ。
# Phase5 Step3-2: QueueRepositoryを副作用として接続する。
#         既存のin-memory EventQueueは並存させたまま残す。QueueRepositoryへの書き込みは
#         QUEUE_EVENT判定済みのイベントに対する追加ログであり、制御ロジックには関与しない。
# Phase5 Step3-3: SnapshotRepositoryをperiodic checkpointとして接続する。
#         ReplayEngine(replay_engine.py)には一切触れない。SnapshotはReplayを変更するものではなく、
#         将来のReplay起点を作るための独立したcheckpoint層であり、自律ロジックを持たない。
# Phase5 Phase4 Step4: ReplayRouterによる経路選択を追加する。
#         これは構造変更ではない。set_replay_mode()/replay()はReplayの入口を差し替えるだけで、
#         ingest()・reduce()・state machine・snapshot/queue/event構造には一切触れない。
#         デフォルトはLEGACY(v1)固定で既存挙動を変えない。
# Phase4.5: ReplayAuditLogを追加し、hybridモードでのDrift検知+記録を可能にする。
#         ingest()/reduce()/state machineには触れない。監査はReplayRouter経由でのみ発生する。

from .policy_engine import PolicyEngine
from .action_router import ActionRouter
from .event_queue import EventQueue
from .replay_engine import ReplayEngine
from .replay_engine_v2 import ReplayEngineV2
from .replay_router import ReplayRouter, LEGACY
from .replay_audit import ReplayAuditLog
from .repositories_sqlite import (
    LocalEventRepository,
    LocalQueueRepository,
    LocalSnapshotRepository,
)

import uuid


class RelayKernel:
    SNAPSHOT_INTERVAL = 100

    def __init__(self, event_repository=None, queue_repository=None, snapshot_repository=None):
        self.state = {}
        self.history = []
        self.policy = PolicyEngine()
        self.action_router = ActionRouter()
        self.queue = EventQueue()
        self.replay_engine = ReplayEngine(self)
        self.event_repository = event_repository or LocalEventRepository()
        self.queue_repository = queue_repository or LocalQueueRepository()
        self.snapshot_repository = snapshot_repository or LocalSnapshotRepository()
        self.replay_engine_v2 = ReplayEngineV2(self, self.snapshot_repository, self.event_repository)
        self.replay_audit_log = ReplayAuditLog()
        self.replay_router = ReplayRouter(self, mode=LEGACY, audit_log=self.replay_audit_log)

    def ingest(self, event: dict) -> dict:
        self.history.append(event)
        self.event_repository.append_event(event)
        self.state = self.reduce(event, self.state)
        decision = self.policy.evaluate(self.state)
        action = self.action_router.route(self.state, decision)

        if action["action"] == "QUEUE_EVENT":
            self.queue.push(event)
            self.queue_repository.push(event)

        self.maybe_snapshot()

        return {
            "state": self.state,
            "policy": decision,
            "action": action,
        }

    def set_replay_mode(self, mode: str) -> None:
        self.replay_router.set_mode(mode)

    def replay(self) -> dict:
        return self.replay_router.replay()

    def maybe_snapshot(self) -> None:
        event_count = self.state.get("event_count", 0)
        if event_count > 0 and event_count % self.SNAPSHOT_INTERVAL == 0:
            self.snapshot_repository.save_snapshot({
                "snapshot_id": str(uuid.uuid4()),
                "node_id": "local",
                "state": self.state,
                "last_event_id": str(event_count),
            })

    def reduce(self, event: dict, state: dict) -> dict:
        return {
            "last_type": event.get("type"),
            "last_source": event.get("source"),
            "event_count": state.get("event_count", 0) + 1,
        }
