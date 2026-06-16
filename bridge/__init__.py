# bridge/__init__.py
from bridge.conflict_types import ConflictJudgment, ConflictState, ConflictResult, BridgeRecord
from bridge.conflict_engine import ConflictEngine
from bridge.mapping_registry import MappingRegistry
from bridge.phi_personal_bridge import PhiPersonalBridge
from bridge.auto_mapper import AutoMapper

__all__ = [
    "ConflictJudgment",
    "ConflictState",
    "ConflictResult",
    "BridgeRecord",
    "ConflictEngine",
    "MappingRegistry",
    "PhiPersonalBridge",
    "AutoMapper",
]
