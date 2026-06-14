"""
MoCKA Core Kernel — phios_integration

責務:
  PHI-OSがPrism(Cognition Layer)を呼び出すための接続層。

  Memory/Relay/Orchestraへの連携は行わない。
  PHI-OSは本モジュール経由で取得した認知結果を保持・返却するのみ。
"""

from .error_info import ErrorInfo
from .exceptions import (
    EventValidationError,
    PhiosIntegrationError,
    ProviderNotInitializedError,
)
from .adapters import (
    JsonMemoryAdapter,
    NoOpMemoryAdapter,
    NoOpOrchestraAdapter,
    NoOpRelayAdapter,
)
from .external_interfaces import (
    MemoryWriterInterface,
    OrchestraAdapterInterface,
    RelayAdapterInterface,
)
from .output_contract import (
    STATUS_ERROR,
    STATUS_OK,
    build_error_response,
    build_success_response,
    from_bridge_result,
)
from .prism_bridge import PrismBridge

__all__ = [
    "PrismBridge",
    "PhiosIntegrationError",
    "ProviderNotInitializedError",
    "EventValidationError",
    "ErrorInfo",
    "STATUS_OK",
    "STATUS_ERROR",
    "build_success_response",
    "build_error_response",
    "from_bridge_result",
    "MemoryWriterInterface",
    "RelayAdapterInterface",
    "OrchestraAdapterInterface",
    "JsonMemoryAdapter",
    "NoOpMemoryAdapter",
    "NoOpRelayAdapter",
    "NoOpOrchestraAdapter",
]
