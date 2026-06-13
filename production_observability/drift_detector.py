"""Phase 7: detects slow degradation (drift) rather than hard crashes.

Drift is a trend, not a single event — each metric is tracked as a rolling
baseline vs. a recent window, and a DriftEvent fires when the recent window
deviates from the baseline beyond threshold.
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from typing import Optional

from event_stream_collector import EventStreamCollector
from system_health_monitor import SystemHealthMonitor
from telemetry_registry import DriftEvent, EventType, Severity, TelemetryEvent

_BASELINE_WINDOW = 100
_RECENT_WINDOW = 20


class DriftDetector:
    def __init__(
        self,
        collector: EventStreamCollector,
        health_monitor: SystemHealthMonitor,
        warning_threshold: float = 0.1,
        critical_threshold: float = 0.25,
    ) -> None:
        self._lock = threading.Lock()
        self._collector = collector
        self._health_monitor = health_monitor
        self._warning_threshold = warning_threshold
        self._critical_threshold = critical_threshold

        self._consistency: dict[str, deque] = defaultdict(lambda: deque(maxlen=_BASELINE_WINDOW))
        self._intent_misclass: dict[str, deque] = defaultdict(lambda: deque(maxlen=_BASELINE_WINDOW))
        self._memory_bias: dict[str, deque] = defaultdict(lambda: deque(maxlen=_BASELINE_WINDOW))
        self._priority: dict[str, deque] = defaultdict(lambda: deque(maxlen=_BASELINE_WINDOW))

        self._drift_events: list[DriftEvent] = []
        collector.subscribe(self._on_event)

    def _on_event(self, event: TelemetryEvent) -> None:
        if event.event_type != EventType.DECISION:
            return

        layer = event.layer
        payload = event.payload

        if "consistency_score" in payload:
            self._check_metric(self._consistency, layer, "consistency_score", float(payload["consistency_score"]), lower_is_worse=True)
        if "intent_misclassified" in payload:
            self._check_metric(self._intent_misclass, layer, "semantic_intent_misclassification", float(payload["intent_misclassified"]), lower_is_worse=False)
        if "memory_retrieval_bias" in payload:
            self._check_metric(self._memory_bias, layer, "memory_retrieval_bias_shift", float(payload["memory_retrieval_bias"]), lower_is_worse=False)
        if "decision_priority" in payload:
            self._check_metric(self._priority, layer, "decision_priority_drift", float(payload["decision_priority"]), lower_is_worse=False)

    def _check_metric(self, store: dict[str, deque], layer: str, metric: str, value: float, lower_is_worse: bool) -> None:
        with self._lock:
            series = store[layer]
            series.append(value)
            if len(series) < _RECENT_WINDOW + 5:
                return

            baseline_slice = list(series)[: -_RECENT_WINDOW]
            recent_slice = list(series)[-_RECENT_WINDOW:]
            baseline = sum(baseline_slice) / len(baseline_slice)
            recent = sum(recent_slice) / len(recent_slice)

            delta = (baseline - recent) if lower_is_worse else (recent - baseline)
            if delta <= self._warning_threshold:
                return

            severity = Severity.CRITICAL if delta >= self._critical_threshold else Severity.WARNING
            drift = DriftEvent.create(
                metric=metric,
                layer=layer,
                severity=severity,
                baseline=round(baseline, 4),
                current=round(recent, 4),
                detail={"delta": round(delta, 4)},
            )
            self._drift_events.append(drift)

        self._collector.emit(
            TelemetryEvent.create(
                EventType.DRIFT,
                layer=layer,
                payload={"drift_id": drift.drift_id, "metric": metric, "severity": severity.value,
                         "baseline": drift.baseline, "current": drift.current},
                severity=severity,
            )
        )

    def drift_events(self) -> list[DriftEvent]:
        with self._lock:
            return list(self._drift_events)

    def latest_drift(self) -> Optional[DriftEvent]:
        with self._lock:
            return self._drift_events[-1] if self._drift_events else None
