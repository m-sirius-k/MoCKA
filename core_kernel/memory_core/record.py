"""
MoCKA Core Kernel — memory_core.record

責務:
  MemoryStoreに保存されるレコードの標準構造(MemoryRecord)を定義する。

  全保存データは以下の構造を持つ:
    {
      "id": str,
      "type": str,
      "timestamp": str,
      "version": "1.0",
      "session_id": str | None,
      "payload": object
    }
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

MEMORY_RECORD_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class MemoryRecord:
    """MemoryStoreに保存される単一レコード。"""

    type: str
    payload: object
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = MEMORY_RECORD_SCHEMA_VERSION
    session_id: str = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "version": self.version,
            "session_id": self.session_id,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            version=data.get("version", MEMORY_RECORD_SCHEMA_VERSION),
            session_id=data.get("session_id"),
            payload=data.get("payload"),
        )
