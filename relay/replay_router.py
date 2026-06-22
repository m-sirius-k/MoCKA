# relay/replay_router.py
# Relay Phase5 Phase4 Step4 - Replayの「経路選択」層。
#
# 絶対条件:
#   - これは構造変更ではない。Replayの入口を差し替えるだけ。
#   - kernel/snapshot/queue/event構造には一切触れない。
#   - migration処理は行わない（v1/v2は常に同じevent_repository/snapshot_repositoryを参照する）。

LEGACY = "v1"
EXPERIMENTAL = "v2"
HYBRID = "hybrid"


class ReplayRouter:
    def __init__(self, kernel, mode: str = LEGACY):
        self.kernel = kernel
        self.mode = mode

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def replay(self) -> dict:
        if self.mode == LEGACY:
            return self._replay_v1()

        if self.mode == EXPERIMENTAL:
            return self._replay_v2()

        if self.mode == HYBRID:
            return self._replay_hybrid()

        raise ValueError(f"unknown replay mode: {self.mode}")

    def _replay_v1(self) -> dict:
        result = self.kernel.replay_engine.replay_all()
        return {"mode": LEGACY, "final_state": result["final_state"], "v1": result}

    def _replay_v2(self) -> dict:
        result = self.kernel.replay_engine_v2.replay_from_snapshot()
        return {"mode": EXPERIMENTAL, "final_state": result["final_state"], "v2": result}

    def _replay_hybrid(self) -> dict:
        v1_result = self.kernel.replay_engine.replay_all()
        v2_result = self.kernel.replay_engine_v2.replay_from_snapshot()
        match = v1_result["final_state"] == v2_result["final_state"]

        return {
            "mode": HYBRID,
            "final_state": v1_result["final_state"],
            "v1": v1_result,
            "v2": v2_result,
            "match": match,
        }
