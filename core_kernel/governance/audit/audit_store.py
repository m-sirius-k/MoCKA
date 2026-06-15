"""Audit Store.

Append-only persistence for AuditRecord. JSON Lines on disk today;
the interface is narrow enough (append/query) to back with another
store (DB) later without touching audit_logger or runtime.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .audit_schema import AuditRecord


class AuditStore:
    """Append-only JSONL audit trail."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, record: AuditRecord) -> None:
        line = json.dumps(asdict(record), ensure_ascii=False)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def all(self) -> list[AuditRecord]:
        return list(self._iter_all())

    def query(self, event_id: str) -> list[AuditRecord]:
        return [r for r in self._iter_all() if r.event_id == event_id]

    def _iter_all(self):
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield AuditRecord(**json.loads(line))
