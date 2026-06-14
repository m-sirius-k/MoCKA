"""
MoCKA Core Kernel — relay_core.relay_session

責務:
  単一セッションにおける時間的文脈の連なり(RelaySession)を表す。

  Relayは「記憶」ではなく「流れ」を扱う。
  本モジュールは永続化を行わない(インメモリ構造のみ)。
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

RELAY_SESSION_SCHEMA_VERSION = "1.0"


@dataclass
class RelaySession:
    """セッション単位の時間的文脈チェーン(インメモリ)。"""

    session_id: str
    event_ids: list = field(default_factory=list)
    context_chain: list = field(default_factory=list)
    timestamps: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    version: str = RELAY_SESSION_SCHEMA_VERSION

    def append_context(self, context, timestamp: str = None) -> None:
        """Contextをcontext_chainに追加し、event_ids/timestampsを更新する。

        Args:
            context: to_dict()を持つPrism Context、またはdict
            timestamp: 省略時は現在時刻(UTC ISO8601)
        """
        context_dict = context.to_dict() if hasattr(context, "to_dict") else dict(context)

        self.context_chain.append(context_dict)

        for event_id in context_dict.get("event_ids", []):
            if event_id not in self.event_ids:
                self.event_ids.append(event_id)

        self.timestamps.append(timestamp or datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "event_ids": list(self.event_ids),
            "context_chain": list(self.context_chain),
            "timestamps": list(self.timestamps),
            "metadata": dict(self.metadata),
            "version": self.version,
        }
