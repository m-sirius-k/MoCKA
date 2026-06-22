# relay/replay_router.py
# Relay Phase5 Phase4 Step4 - Replayの「経路選択」層。
#
# 絶対条件:
#   - これは構造変更ではない。Replayの入口を差し替えるだけ。
#   - kernel/snapshot/queue/event構造には一切触れない。
#   - migration処理は行わない（v1/v2は常に同じevent_repository/snapshot_repositoryを参照する）。
#
# Phase4.5: hybridモードにReplay監査(Drift検知+Audit Log記録)を統合する。
#   - 戻り値はreturn_v1原則(final_stateはv1側)を維持する。監査はログ記録のみ。

from .replay_audit import compute_state_hash

LEGACY = "v1"
EXPERIMENTAL = "v2"
HYBRID = "hybrid"


class ReplayRouter:
    def __init__(self, kernel, mode: str = LEGACY, audit_log=None):
        self.kernel = kernel
        self.mode = mode
        self.audit_log = audit_log

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

        if self.audit_log is not None:
            event_hash = compute_state_hash({
                "v1_event_count": len(v1_result.get("snapshots", [])),
                "v2_delta_count": v2_result.get("delta_count"),
            })
            state_hash = compute_state_hash(v1_result["final_state"])
            self.audit_log.record(
                replay_mode=HYBRID,
                event_hash=event_hash,
                state_hash=state_hash,
                match=match,
            )
            if not match:
                self._emit_drift(v1_result["final_state"], v2_result["final_state"])

        return {
            "mode": HYBRID,
            "final_state": v1_result["final_state"],
            "v1": v1_result,
            "v2": v2_result,
            "match": match,
        }

    def _emit_drift(self, v1_state: dict, v2_state: dict) -> None:
        # REPLAY_DRIFT: v1とv2が不一致。記録のみ行い、自動修復はしない(最小実装スコープ外)。
        print(f"[REPLAY_DRIFT] v1={v1_state} v2={v2_state}")
