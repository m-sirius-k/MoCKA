"""
MoCKA Core Kernel — phios_integration

責務:
  PHI-OSがPrism(Cognition Layer)を呼び出すための接続層。

  Memory/Relay/Orchestraへの連携は行わない。
  PHI-OSは本モジュール経由で取得した認知結果を保持・返却するのみ。
"""

from .exceptions import (
    EventValidationError,
    PhiosIntegrationError,
    ProviderNotInitializedError,
)
from .prism_bridge import PrismBridge

__all__ = [
    "PrismBridge",
    "PhiosIntegrationError",
    "ProviderNotInitializedError",
    "EventValidationError",
]
