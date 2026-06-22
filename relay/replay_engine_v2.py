# relay/replay_engine_v2.py
# Relay Phase5 Phase4 Step1 - Snapshot-aware Replay(Option A: 非破壊並列実装)。
#
# 既存のReplayEngine(replay_engine.py)は変更しない。本クラスはそれとは別の
# 新しい時間再構築方式(Snapshot起点 + Event delta補完)を提供する独立クラスである。
#
# Before(既存ReplayEngine): Event全列スキャン -> state再構築
# After(本クラス):          Snapshot起点 + Event delta補完 -> state再構築
#
# 絶対条件:
#   - 既存ReplayEngine/RelayKernel.ingestには一切触れない
#   - Queueには関与しない(実行系はPhase5の別領域として維持)
#   - スナップショットが無い場合はevent_repositoryの全件からfull replayにフォールバックする

import copy


class ReplayEngineV2:
    def __init__(self, kernel, snapshot_repository, event_repository):
        self.kernel = kernel
        self.snapshot_repository = snapshot_repository
        self.event_repository = event_repository

    def replay_from_snapshot(self) -> dict:
        snapshot = self.snapshot_repository.load_latest()

        if snapshot is None:
            return self._replay_full()

        state = copy.deepcopy(snapshot["state"])
        delta_records = self.event_repository.get_events(from_id=snapshot["last_event_id"])

        snapshots = []
        for record in delta_records:
            state = self.kernel.reduce(record["event"], state)
            snapshots.append({
                "event": record["event"],
                "state": copy.deepcopy(state),
            })

        return {
            "final_state": state,
            "snapshot_used": snapshot,
            "delta_count": len(delta_records),
            "snapshots": snapshots,
        }

    def _replay_full(self) -> dict:
        state = {}
        snapshots = []

        for record in self.event_repository.get_events():
            state = self.kernel.reduce(record["event"], state)
            snapshots.append({
                "event": record["event"],
                "state": copy.deepcopy(state),
            })

        return {
            "final_state": state,
            "snapshot_used": None,
            "delta_count": len(snapshots),
            "snapshots": snapshots,
        }
