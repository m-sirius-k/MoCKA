"""
MoCKA Core Kernel — relay_core

責務:
  時間的文脈とセッション連続性を管理する層(Relay)。

  Relayは「記憶」ではなく「流れ」を扱う。インメモリ管理のみであり、
  永続化(DB/JSON/file)・Memory書き込み・AI/LLM呼び出し・
  Orchestra連携・Workflow制御は行わない。
"""

from .relay_session import RELAY_SESSION_SCHEMA_VERSION, RelaySession
from .session_relay import SessionRelay

__all__ = [
    "SessionRelay",
    "RelaySession",
    "RELAY_SESSION_SCHEMA_VERSION",
]
