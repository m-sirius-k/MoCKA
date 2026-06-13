"""Phase 7: structured internal model for an external dashboard to render.

Not a UI — a snapshot of system_health, drift_map, failure_heatmap and
layer_stability_index, all derived from observability components.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from control_policy_engine import ControlPolicyEngine
from drift_detector import DriftDetector
from system_health_monitor import SystemHealthMonitor
from telemetry_aggregator import TelemetryAggregator


@dataclass(frozen=True)
class DashboardSnapshot:
    system_health_score: float
    layer_health: dict[str, dict]
    drift_map: list[dict]
    failure_heatmap: dict[str, int]
    layer_stability_index: dict[str, float]
    control_decisions: list[dict]


class ProductionDashboardModel:
    def __init__(
        self,
        aggregator: TelemetryAggregator,
        health_monitor: SystemHealthMonitor,
        drift_detector: DriftDetector,
        control_engine: ControlPolicyEngine,
    ) -> None:
        self._aggregator = aggregator
        self._health_monitor = health_monitor
        self._drift_detector = drift_detector
        self._control_engine = control_engine

    def snapshot(self) -> DashboardSnapshot:
        layers = self._health_monitor.layers()

        layer_health = {
            layer: vars(self._health_monitor.layer_health(layer)) for layer in layers
        }

        drift_map = [
            {
                "drift_id": d.drift_id,
                "metric": d.metric,
                "layer": d.layer,
                "severity": d.severity.value,
                "baseline": d.baseline,
                "current": d.current,
            }
            for d in self._drift_detector.drift_events()
        ]

        failure_heatmap: dict[str, int] = {}
        from telemetry_registry import EventType
        for layer in layers:
            failures = [e for e in self._aggregator.events_for_layer(layer) if e.event_type == EventType.FAILURE]
            failure_heatmap[layer] = len(failures)

        layer_stability_index = {
            layer: round(1.0 - layer_health[layer]["failure_rate"], 4) for layer in layers
        }

        control_decisions = [
            {
                "action": d.action.value,
                "layer": d.layer,
                "reason": d.reason,
                "drift_id": d.drift_id,
                "decided_at": d.decided_at,
            }
            for d in self._control_engine.decisions()
        ]

        return DashboardSnapshot(
            system_health_score=self._health_monitor.system_health_score(),
            layer_health=layer_health,
            drift_map=drift_map,
            failure_heatmap=failure_heatmap,
            layer_stability_index=layer_stability_index,
            control_decisions=control_decisions,
        )
