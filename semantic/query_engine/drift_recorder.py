"""
Phase10-4: Operational Observation Layer - minimal implementation.

Scope (per docs/contracts/phase10_4_operational_observation_layer_v1.md):
  - log format codification only (no interpretation logic)
  - single fixed storage location (no replication, no distribution)
  - optional pass-through to mocka_write_event (no semantic enrichment)

Permanently forbidden in this module (per Human Gate ruling, monitor R01):
  - drift interpretation / meaning analysis / evaluation functions
  - polling, continuous inference, guess-based detection
  - any code that scores, judges, or explains a drift
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DRIFT_TYPES = ("STRUCTURE", "SEMANTIC", "OPERATIONAL")

DEFAULT_DB_PATH = Path("data/phase10/drift_log.db")


@dataclass(frozen=True)
class DriftRecord:
    event_id: str
    target: str
    drift_type: str
    before_ref: str
    after_ref: str
    timestamp: str

    def __post_init__(self) -> None:
        if self.drift_type not in DRIFT_TYPES:
            raise ValueError(f"drift_type must be one of {DRIFT_TYPES}")


class DriftRecorder:
    """Single-source, single-writer drift event recorder.

    No polling, no background loop. record() is only invoked explicitly
    by the four trigger sources (Git state change / Event log write /
    File structure change / Semantic declaration change).
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS drift_log (
                    event_id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    drift_type TEXT NOT NULL,
                    before_ref TEXT NOT NULL,
                    after_ref TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )

    def record(
        self,
        event_id: str,
        target: str,
        drift_type: str,
        before_ref: str,
        after_ref: str,
        timestamp: Optional[str] = None,
    ) -> DriftRecord:
        rec = DriftRecord(
            event_id=event_id,
            target=target,
            drift_type=drift_type,
            before_ref=before_ref,
            after_ref=after_ref,
            timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO drift_log "
                "(event_id, target, drift_type, before_ref, after_ref, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (rec.event_id, rec.target, rec.drift_type, rec.before_ref, rec.after_ref, rec.timestamp),
            )
        return rec

    def get_all(self) -> list[DriftRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_id, target, drift_type, before_ref, after_ref, timestamp "
                "FROM drift_log ORDER BY timestamp ASC"
            ).fetchall()
        return [DriftRecord(*row) for row in rows]


def to_write_event_payload(rec: DriftRecord) -> dict:
    """Pure field pass-through for mocka_write_event. No semantic enrichment."""
    return {
        "title": f"DRIFT_RECORDED: {rec.drift_type} {rec.target}",
        "description": (
            f"event_id={rec.event_id}\n"
            f"target={rec.target}\n"
            f"drift_type={rec.drift_type}\n"
            f"before_ref={rec.before_ref}\n"
            f"after_ref={rec.after_ref}\n"
            f"timestamp={rec.timestamp}"
        ),
        "tags": f"phase10-4,drift,{rec.drift_type.lower()}",
    }
