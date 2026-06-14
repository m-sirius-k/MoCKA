"""
MoCKA Core Kernel — memory_core

責務:
  AnalysisResult / Context / Observation / CognitiveState を
  永続化するための最小永続化層(Minimal Persistence Layer)。

  JSON file store (推奨) または in-memory fallback を提供する。
  外部DB/Redis/Network通信/LLM/Workflow制御は行わない。
"""

from .memory_store import MemoryStore
from .record import MEMORY_RECORD_SCHEMA_VERSION, MemoryRecord

__all__ = [
    "MemoryStore",
    "MemoryRecord",
    "MEMORY_RECORD_SCHEMA_VERSION",
]
