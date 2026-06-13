"""Phase 7: shared event/trace schema definitions (no hidden state, no logs)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EventType(str, Enum):
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    LAYER_ENTER = "layer_enter"
    LAYER_EXIT = "layer_exit"
    DECISION = "decision"
    FAILURE = "failure"
    DRIFT = "drift"
    CONTROL_ACTION = "control_action"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TelemetryEvent:
    """Atomic, immutable unit of observability. Never mutated after creation."""

    event_id: str
    event_type: EventType
    layer: str
    timestamp: float
    request_id: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)
    severity: Severity = Severity.INFO

    @staticmethod
    def create(
        event_type: EventType,
        layer: str,
        request_id: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        severity: Severity = Severity.INFO,
    ) -> "TelemetryEvent":
        return TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            layer=layer,
            timestamp=time.time(),
            request_id=request_id,
            payload=payload or {},
            severity=severity,
        )


@dataclass(frozen=True)
class DriftEvent:
    drift_id: str
    metric: str
    layer: str
    severity: Severity
    baseline: float
    current: float
    detected_at: float
    detail: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(metric: str, layer: str, severity: Severity, baseline: float,
               current: float, detail: Optional[dict[str, Any]] = None) -> "DriftEvent":
        return DriftEvent(
            drift_id=str(uuid.uuid4()),
            metric=metric,
            layer=layer,
            severity=severity,
            baseline=baseline,
            current=current,
            detected_at=time.time(),
            detail=detail or {},
        )


@dataclass(frozen=True)
class TraceObject:
    request_id: str
    started_at: float
    ended_at: Optional[float]
    path: list[str]
    decisions: list[dict[str, Any]]
    failures: list[dict[str, Any]]

    @property
    def duration(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return self.ended_at - self.started_at
