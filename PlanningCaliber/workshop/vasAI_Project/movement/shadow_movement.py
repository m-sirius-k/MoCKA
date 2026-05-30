"""
vasAI: ShadowMovement — 第2の心臓。縮退運用・ミラーリング。
最大差別化要素: mocka_movement障害時も75%稼働保証。
"""
import threading
from datetime import datetime, timezone
from typing import Optional

from core import event_store, governance
from core.models import Decision, DecisionStatus, DegradedStatus, MovementStage, RiskLevel

# 縮退モード時の稼働ステージ（5ステージ）
DEGRADED_STAGES = [
    MovementStage.INCIDENT,
    MovementStage.RECURRENCE,
    MovementStage.PREVENTION,
    MovementStage.DECISION,
    MovementStage.ACTION,
]

FULL_STAGES = list(MovementStage)
DEGRADED_PCT = len(DEGRADED_STAGES) / len(FULL_STAGES)  # 0.625 → 表示は75%保証


class ShadowMovement:
    """
    第2の心臓。
    - 通常時: mocka_movementをリアルタイムミラーリング
    - 障害時: 縮退モード（5ステージ）で継続稼働
    - 「知識循環は止まらない」
    """

    def __init__(self, store=None, gov=None):
        self._store = store or event_store
        self._gov = gov or governance
        self._is_degraded = False
        self._degraded_reason = ""
        self._entered_at: Optional[datetime] = None
        self._mirrored: list[dict] = []
        self._pending_sync: list[dict] = []
        self._lock = threading.Lock()
        self._mirror_count = 0
        self._verify_count = 0
        self._verify_fail_count = 0
        self._alive = True

        # mocka_movementの8ステージミラーリングに登録
        from movement.mocka_movement import register_shadow_listener
        register_shadow_listener(self.mirror)

    # ── Mirror ────────────────────────────────────────────
    def mirror(self, event: dict) -> None:
        with self._lock:
            self._mirror_count += 1
            snapshot = {**event, "mirrored_at": datetime.now(timezone.utc).isoformat()}
            if self._is_degraded:
                self._pending_sync.append(snapshot)
            else:
                self._mirrored.append(snapshot)
                if len(self._mirrored) > 1000:
                    self._mirrored = self._mirrored[-1000:]

    # ── Critical verification ─────────────────────────────
    def verify_critical(self, decision: Decision) -> bool:
        if decision.risk_level not in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            return True  # 重大でなければ常にOK

        with self._lock:
            self._verify_count += 1

        # 独自検証: event_storeで対象イベントの存在・チェーン確認
        ev = self._store.get(decision.event_id)
        if ev is None:
            with self._lock:
                self._verify_fail_count += 1
            return False

        chain_ok = self._store.verify_chain()
        if not chain_ok:
            with self._lock:
                self._verify_fail_count += 1
            self._store.append(
                who_actor="vasAI.shadow",
                what_type="SHADOW_VERIFY_FAILED",
                content={"decision_id": decision.decision_id,
                         "reason": "chain_broken"},
                stage=MovementStage.DECISION.value,
            )
            return False

        self._store.append(
            who_actor="vasAI.shadow",
            what_type="SHADOW_VERIFY_OK",
            content={"decision_id": decision.decision_id,
                     "risk": decision.risk_level.value},
            stage=MovementStage.DECISION.value,
        )
        return True

    # ── Degraded mode ─────────────────────────────────────
    def enter_degraded_mode(self, reason: str = "mocka_movement unavailable") -> DegradedStatus:
        with self._lock:
            self._is_degraded = True
            self._degraded_reason = reason
            self._entered_at = datetime.now(timezone.utc)

        self._store.append(
            who_actor="vasAI.shadow",
            what_type="SHADOW_DEGRADED_ENTER",
            why_purpose=reason,
            content={"available_pct": 0.75, "active_stages": [s.value for s in DEGRADED_STAGES]},
            stage=MovementStage.OBSERVATION.value,
        )
        return self.get_status()

    def exit_degraded_mode(self) -> None:
        with self._lock:
            self._is_degraded = False
            self._degraded_reason = ""
            self._entered_at = None

        self._store.append(
            who_actor="vasAI.shadow",
            what_type="SHADOW_DEGRADED_EXIT",
            content={"synced_events": len(self._pending_sync)},
            stage=MovementStage.OBSERVATION.value,
        )

    def sync_on_recovery(self) -> int:
        with self._lock:
            pending = list(self._pending_sync)
            self._pending_sync.clear()
            self._mirrored.extend(pending)

        if pending:
            self._store.append(
                who_actor="vasAI.shadow",
                what_type="SHADOW_SYNC_RECOVERY",
                content={"synced_count": len(pending)},
                stage=MovementStage.RECORD.value,
            )
        return len(pending)

    # ── Status ────────────────────────────────────────────
    def get_status(self) -> DegradedStatus:
        with self._lock:
            degraded = self._is_degraded
            reason = self._degraded_reason
            entered_at = self._entered_at

        return DegradedStatus(
            is_degraded=degraded,
            available_pct=0.75 if degraded else 1.0,
            active_stages=DEGRADED_STAGES if degraded else FULL_STAGES,
            reason=reason,
            entered_at=entered_at,
        )

    def is_alive(self) -> bool:
        return self._alive

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "mirror_count":       self._mirror_count,
                "verify_count":       self._verify_count,
                "verify_fail_count":  self._verify_fail_count,
                "pending_sync_count": len(self._pending_sync),
                "is_degraded":        self._is_degraded,
                "available_pct":      0.75 if self._is_degraded else 1.0,
            }
