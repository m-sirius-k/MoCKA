"""Phase 7: reconstructs request-level execution traces from the telemetry stream."""

from __future__ import annotations

from telemetry_aggregator import TelemetryAggregator
from telemetry_registry import EventType, TraceObject


class TraceBuilder:
    def __init__(self, aggregator: TelemetryAggregator) -> None:
        self._aggregator = aggregator

    def build(self, request_id: str) -> TraceObject:
        events = sorted(
            self._aggregator.events_for_request(request_id),
            key=lambda e: e.timestamp,
        )

        path: list[str] = []
        decisions: list[dict] = []
        failures: list[dict] = []
        started_at: float | None = None
        ended_at: float | None = None

        for event in events:
            if event.event_type == EventType.REQUEST_START:
                started_at = event.timestamp
            elif event.event_type == EventType.REQUEST_END:
                ended_at = event.timestamp
            elif event.event_type == EventType.LAYER_ENTER:
                path.append(event.layer)
            elif event.event_type == EventType.DECISION:
                decisions.append({"layer": event.layer, "timestamp": event.timestamp, **event.payload})
            elif event.event_type == EventType.FAILURE:
                failures.append({"layer": event.layer, "timestamp": event.timestamp, **event.payload})

        if started_at is None and events:
            started_at = events[0].timestamp

        return TraceObject(
            request_id=request_id,
            started_at=started_at or 0.0,
            ended_at=ended_at,
            path=path,
            decisions=decisions,
            failures=failures,
        )

    def build_all(self) -> list[TraceObject]:
        request_ids = {e.request_id for e in self._aggregator.timeline() if e.request_id}
        return [self.build(rid) for rid in request_ids]
