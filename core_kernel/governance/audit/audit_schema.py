"""Audit Schema.

The type of evidence. One AuditRecord answers one "judgement" question:
who decided what, on what rule, why, and when. Audit never derives new
meaning beyond restructuring the fields below — it is the shape of the
record, not a policy.
"""

from __future__ import annotations

from dataclasses import dataclass

CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class AuditRecord:
    """A single, immutable audit entry.

    Fields (fixed, per くろこ指示書 Phase 4):
        event_id  - Event ID
        engine    - Engine that produced this entry
        rule      - Rule / scope / category / contract identifier
        decision  - Decision or status value, recorded as-is (str)
        reason    - Reason / evidence summary, recorded as-is (str)
        timestamp - ISO8601 timestamp of the source record
        version   - Contract version of the source record
    """

    event_id: str
    engine: str
    rule: str
    decision: str
    reason: str
    timestamp: str
    version: str

    def __post_init__(self) -> None:
        for field_name in ("event_id", "engine", "rule", "decision", "timestamp", "version"):
            if not getattr(self, field_name):
                raise ValueError(f"AuditRecord.{field_name} is required")
