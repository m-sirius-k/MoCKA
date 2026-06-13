# -*- coding: utf-8 -*-
"""Failure Containment System (Phase 6 Commercial Hardening Layer)

設計:
  - failure zone segmentation     : システムをzone単位に分割し、障害を局所化する
  - cascading failure prevention  : あるzoneの障害が他zoneのcontain()呼び出しに伝播しない
  - local rollback only           : zone内のrollback_funcのみを実行する
    (他zone・グローバル状態へのrollbackは行わない)
"""

from dataclasses import dataclass, field

from commercial_hardening import safe_fallback_engine


@dataclass
class ZoneState:
    zone_id: str
    healthy: bool = True
    last_error: str = ""
    failure_count: int = 0


class FailureContainmentRegistry:
    """zone_id -> ZoneState の登録簿。インスタンスごとに独立 (グローバル状態を持たない)。"""

    def __init__(self):
        self._zones: dict[str, ZoneState] = {}

    def get(self, zone_id: str) -> ZoneState:
        return self._zones.setdefault(zone_id, ZoneState(zone_id=zone_id))

    def contain(self, zone_id: str, func, rollback_func=None, fallback_kind: str = "default"):
        """funcをzone内で実行する。失敗時はそのzoneのみhealthy=Falseにし、
        rollback_func (存在する場合) をzoneローカルに実行する。
        例外は他zoneへ伝播しない (cascading failure prevention)。
        """
        zone = self.get(zone_id)
        try:
            value = func()
            return value
        except Exception as exc:  # noqa: BLE001 - failure zone境界
            zone.healthy = False
            zone.failure_count += 1
            zone.last_error = repr(exc)

            if rollback_func is not None:
                try:
                    rollback_func()
                except Exception as rollback_exc:  # noqa: BLE001
                    zone.last_error += f" | rollback_failed: {rollback_exc!r}"

            return safe_fallback_engine.fallback(zone_id, fallback_kind, reason=repr(exc))

    def healthy_zones(self) -> list:
        return [z.zone_id for z in self._zones.values() if z.healthy]

    def unhealthy_zones(self) -> list:
        return [z.zone_id for z in self._zones.values() if not z.healthy]

    def overall_healthy(self) -> bool:
        return all(z.healthy for z in self._zones.values())
