"""Phase 7: continuous, event-driven health scoring per layer and system-wide."""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from dataclasses import dataclass

from event_stream_collector import EventStreamCollector
from telemetry_registry import EventType, TelemetryEvent

_WINDOW = 200  # rolling sample size per layer


@dataclass(frozen=True)
class LayerHealth:
    layer: str
    failure_rate: float
    avg_latency: float
    consistency_score: float
    queue_backlog: int
    health_score: float


class SystemHealthMonitor:
    """Subscribes to the event stream; recomputes scores incrementally on each event."""

    def __init__(self, collector: EventStreamCollector) -> None:
        self._lock = threading.Lock()
        self._failures: dict[str, deque] = defaultdict(lambda: deque(maxlen=_WINDOW))
        self._latencies: dict[str, deque] = defaultdict(lambda: deque(maxlen=_WINDOW))
        self._consistency: dict[str, deque] = defaultdict(lambda: deque(maxlen=_WINDOW))
        self._queue_backlog: dict[str, int] = defaultdict(int)
        self._enter_times: dict[tuple[str, str], float] = {}
        collector.subscribe(self._on_event)

    def _on_event(self, event: TelemetryEvent) -> None:
        with self._lock:
            layer = event.layer
            if event.event_type == EventType.LAYER_ENTER:
                self._queue_backlog[layer] += 1
                if event.request_id:
                    self._enter_times[(layer, event.request_id)] = event.timestamp
            elif event.event_type == EventType.LAYER_EXIT:
                self._queue_backlog[layer] = max(0, self._queue_backlog[layer] - 1)
                key = (layer, event.request_id)
                if event.request_id and key in self._enter_times:
                    latency = event.timestamp - self._enter_times.pop(key)
                    self._latencies[layer].append(latency)
                self._failures[layer].append(0)
            elif event.event_type == EventType.FAILURE:
                self._failures[layer].append(1)
            elif event.event_type == EventType.DECISION:
                score = event.payload.get("consistency_score")
                if score is not None:
                    self._consistency[layer].append(float(score))

    def layer_health(self, layer: str) -> LayerHealth:
        with self._lock:
            failures = self._failures[layer]
            latencies = self._latencies[layer]
            consistency = self._consistency[layer]
            backlog = self._queue_backlog[layer]

            failure_rate = sum(failures) / len(failures) if failures else 0.0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
            consistency_score = sum(consistency) / len(consistency) if consistency else 1.0

        health_score = max(
            0.0,
            1.0 - failure_rate - min(avg_latency / 10.0, 0.5) - max(0.0, (1.0 - consistency_score)),
        )
        return LayerHealth(
            layer=layer,
            failure_rate=failure_rate,
            avg_latency=avg_latency,
            consistency_score=consistency_score,
            queue_backlog=backlog,
            health_score=round(health_score, 4),
        )

    def layers(self) -> list[str]:
        with self._lock:
            return sorted(set(self._failures) | set(self._latencies) | set(self._consistency) | set(self._queue_backlog))

    def system_health_score(self) -> float:
        layers = self.layers()
        if not layers:
            return 1.0
        scores = [self.layer_health(layer).health_score for layer in layers]
        return round(sum(scores) / len(scores), 4)
