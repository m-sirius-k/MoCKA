"""Requirement History.

An append-only, intent-tagged log of *why* a Requirement (REQ-*) was
created or changed. Distinct from the Audit trail (audit/audit_store):
Audit records what happened at runtime for an Event; this records the
design-time intent behind a Requirement's existence/evolution.

Per くろこ指示書: design documents are not modified by this module —
it only records intent alongside them.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RequirementChange:
    req_id: str
    version: str
    timestamp: str
    change_type: str  # e.g. "CREATED", "REVISED", "SUPERSEDED"
    intent: str  # why this change was made
    description: str

    def __post_init__(self) -> None:
        for field_name in ("req_id", "version", "timestamp", "change_type", "intent"):
            if not getattr(self, field_name):
                raise ValueError(f"RequirementChange.{field_name} is required")


class RequirementHistoryStore:
    """Append-only JSONL store for RequirementChange entries."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, change: RequirementChange) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(change), ensure_ascii=False) + "\n")

    def all(self) -> list[RequirementChange]:
        return list(self._iter_all())

    def query(self, req_id: str) -> list[RequirementChange]:
        return [c for c in self._iter_all() if c.req_id == req_id]

    def _iter_all(self):
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield RequirementChange(**json.loads(line))
