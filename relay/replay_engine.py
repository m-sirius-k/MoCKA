# relay/replay_engine.py
# Relay Phase4 — RelayKernel.history(プロセス内・揮発性のセッション履歴)から
# stateを再構築する時間制御コア。
#
# 注意: phi_os/event_replay.py(EventAuditEngine/EventReplayer)とは別物。
# あちらはDB(data/mocka_events.db)に永続化された本番イベントを対象とする
# 監査用replayであり、本モジュールはRelayKernelの現在のプロセス内
# in-memory historyのみを対象とする揮発性replayである。プロセス再起動で
# historyは消え、本モジュールが再構築できる状態も失われる。

import copy


class ReplayEngine:
    def __init__(self, kernel):
        self.kernel = kernel

    def replay(self, events: list) -> dict:
        state = {}
        snapshots = []

        for event in events:
            state = self.kernel.reduce(event, state)
            snapshots.append({
                "event": event,
                "state": copy.deepcopy(state),
            })

        return {
            "final_state": state,
            "snapshots": snapshots,
        }

    def replay_all(self) -> dict:
        return self.replay(self.kernel.history)
