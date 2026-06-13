"""Phase 7: append-only, event-driven collection of TelemetryEvents.

No polling. No log files. Subscribers are notified synchronously on emit.
"""

from __future__ import annotations

import threading
from typing import Callable, Iterable

from telemetry_registry import TelemetryEvent

Subscriber = Callable[[TelemetryEvent], None]


class EventStreamCollector:
    def __init__(self) -> None:
        self._stream: list[TelemetryEvent] = []
        self._subscribers: list[Subscriber] = []
        self._lock = threading.Lock()

    def subscribe(self, callback: Subscriber) -> None:
        with self._lock:
            self._subscribers.append(callback)

    def emit(self, event: TelemetryEvent) -> None:
        with self._lock:
            self._stream.append(event)
            subscribers = list(self._subscribers)
        for callback in subscribers:
            callback(event)

    def replay(self, since_index: int = 0) -> Iterable[TelemetryEvent]:
        """Replay the append-only stream from a given offset (for event replay tests)."""
        with self._lock:
            return tuple(self._stream[since_index:])

    def __len__(self) -> int:
        with self._lock:
            return len(self._stream)
