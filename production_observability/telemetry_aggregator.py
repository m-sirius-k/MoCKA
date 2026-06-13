"""Phase 7: integrates all layer events into a time-series, correlation-ready stream.

Event-driven only — registers as a subscriber on EventStreamCollector, never polls.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Optional

from event_stream_collector import EventStreamCollector
from telemetry_registry import TelemetryEvent


class TelemetryAggregator:
    def __init__(self, collector: EventStreamCollector) -> None:
        self._lock = threading.Lock()
        self._timeline: list[TelemetryEvent] = []
        self._by_layer: dict[str, list[TelemetryEvent]] = defaultdict(list)
        self._by_request: dict[str, list[TelemetryEvent]] = defaultdict(list)
        collector.subscribe(self._on_event)

    def _on_event(self, event: TelemetryEvent) -> None:
        with self._lock:
            self._timeline.append(event)
            self._by_layer[event.layer].append(event)
            if event.request_id:
                self._by_request[event.request_id].append(event)

    def timeline(self) -> list[TelemetryEvent]:
        with self._lock:
            return list(self._timeline)

    def events_for_layer(self, layer: str) -> list[TelemetryEvent]:
        with self._lock:
            return list(self._by_layer.get(layer, []))

    def events_for_request(self, request_id: str) -> list[TelemetryEvent]:
        with self._lock:
            return list(self._by_request.get(request_id, []))

    def correlate_failures(self, window_seconds: float = 5.0) -> list[list[TelemetryEvent]]:
        """Group FAILURE events that occur within `window_seconds` of each other
        across layers, regardless of request_id (failure correlation mapping)."""
        from telemetry_registry import EventType

        with self._lock:
            failures = sorted(
                (e for e in self._timeline if e.event_type == EventType.FAILURE),
                key=lambda e: e.timestamp,
            )

        groups: list[list[TelemetryEvent]] = []
        for event in failures:
            if groups and event.timestamp - groups[-1][-1].timestamp <= window_seconds:
                groups[-1].append(event)
            else:
                groups.append([event])
        return [g for g in groups if len(g) > 1]
