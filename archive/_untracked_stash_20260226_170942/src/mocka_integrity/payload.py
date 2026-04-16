"""
Deterministic payload utilities
date: 2026-02-24

note:
- Determinism rules:
  - JSON is UTF-8
  - keys sorted
  - separators fixed: (",", ":")
  - no whitespace
  - ensure_ascii=False (but output bytes are UTF-8)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict


def dumps_canonical(obj: Any) -> str:
    """
    Return canonical JSON string.
    """
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def dumps_canonical_bytes(obj: Any) -> bytes:
    """
    Return canonical JSON encoded as UTF-8 bytes.
    """
    return dumps_canonical(obj).encode("utf-8")


@dataclass(frozen=True)
class AnchorPayload:
    """
    Canonical anchor payload fields.
    Keep this minimal and stable.
    """
    source_event_id: str
    source_chain_hash: str
    final_chain_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_event_id": self.source_event_id,
            "source_chain_hash": self.source_chain_hash,
            "final_chain_hash": self.final_chain_hash,
        }

    def canonical_json(self) -> str:
        return dumps_canonical(self.to_dict())

    def canonical_bytes(self) -> bytes:
        return dumps_canonical_bytes(self.to_dict())
