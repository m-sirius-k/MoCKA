"""Event Contract.

Minimal reference shape used by all other contracts to link back to
mocka_write_event records (Event Reference / EVENT_FOUNDATION_v1).
"""

from __future__ import annotations

from dataclasses import dataclass

CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class EventContract:
    """Reference to a recorded MoCKA event."""

    event_id: str
    title: str

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("EventContract.event_id is required")
        if not self.title:
            raise ValueError("EventContract.title is required")
