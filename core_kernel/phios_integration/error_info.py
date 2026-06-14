"""
MoCKA Core Kernel — phios_integration.error_info

責務:
  PHI-OS出力契約における標準エラー構造(ErrorInfo)を定義する。
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ErrorInfo:
    """PHI-OS出力契約における標準エラー構造。"""

    error_type: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = None
    source_module: str = "phios_integration"

    def to_dict(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "source_module": self.source_module,
        }
