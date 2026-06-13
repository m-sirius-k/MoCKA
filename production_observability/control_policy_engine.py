"""Phase 7: control center. Control decisions are derived only from observed
DriftEvents and health scores — never invoked independently of observability.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from drift_detector import DriftDetector
from event_stream_collector import EventStreamCollector
from system_health_monitor import SystemHealthMonitor
from telemetry_registry import DriftEvent, EventType, Severity, TelemetryEvent


class ControlAction(str, Enum):
    NONE = "none"
    THROTTLE = "throttle"
    SAFE_MODE = "safe_mode"
    REROUTE = "reroute"


@dataclass(frozen=True)
class ControlDecision:
    action: ControlAction
    layer: str
    reason: str
    drift_id: Optional[str]
    decided_at: float = field(default_factory=time.time)


# Feedback callback signature: receives a ControlDecision, forwards it to the
# execution router. Kept as a plain callback to avoid coupling this module to
# the router's implementation.
FeedbackCallback = Callable[[ControlDecision], None]


class ControlPolicyEngine:
    def __init__(
        self,
        collector: EventStreamCollector,
        drift_detector: DriftDetector,
        health_monitor: SystemHealthMonitor,
        safe_mode_health_threshold: float = 0.4,
        feedback: Optional[FeedbackCallback] = None,
    ) -> None:
        self._lock = threading.Lock()
        self._collector = collector
        self._health_monitor = health_monitor
        self._safe_mode_health_threshold = safe_mode_health_threshold
        self._feedback = feedback
        self._decisions: list[ControlDecision] = []
        self._safe_mode_layers: set[str] = set()

        collector.subscribe(self._on_event)

    def _on_event(self, event: TelemetryEvent) -> None:
        if event.event_type != EventType.DRIFT:
            return

        layer = event.layer
        severity = Severity(event.payload.get("severity", Severity.WARNING.value))
        drift_id = event.payload.get("drift_id")

        action = self._decide(layer, severity)
        if action == ControlAction.NONE:
            return

        decision = ControlDecision(
            action=action,
            layer=layer,
            reason=f"drift severity={severity.value} health={self._health_monitor.layer_health(layer).health_score}",
            drift_id=drift_id,
        )

        with self._lock:
            self._decisions.append(decision)
            if action == ControlAction.SAFE_MODE:
                self._safe_mode_layers.add(layer)

        self._collector.emit(
            TelemetryEvent.create(
                EventType.CONTROL_ACTION,
                layer=layer,
                payload={"action": action.value, "reason": decision.reason, "drift_id": drift_id},
                severity=severity,
            )
        )

        if self._feedback:
            self._feedback(decision)

    def _decide(self, layer: str, severity: Severity) -> ControlAction:
        health = self._health_monitor.layer_health(layer).health_score
        if health < self._safe_mode_health_threshold:
            return ControlAction.SAFE_MODE
        if severity == Severity.CRITICAL:
            return ControlAction.REROUTE
        if severity == Severity.WARNING:
            return ControlAction.THROTTLE
        return ControlAction.NONE

    def decisions(self) -> list[ControlDecision]:
        with self._lock:
            return list(self._decisions)

    def is_safe_mode(self, layer: str) -> bool:
        with self._lock:
            return layer in self._safe_mode_layers

    def clear_safe_mode(self, layer: str) -> None:
        with self._lock:
            self._safe_mode_layers.discard(layer)
