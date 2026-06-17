# phi_os/context — Context Runtime v2
# Layer1: InstitutionContext  — 制度情報
# Layer2: WorkingContext      — 現在の作業状態
# Layer3: MemoryContext       — AI共通理解
# Layer4: ExecutionContext    — 実装開始判定・Execution Gate
from .institution_context import InstitutionContext
from .working_context import WorkingContext
from .memory_context import MemoryContext
from .execution_context import ExecutionContext, ExecutionGate, GateResult
from .context_runtime import ContextRuntime
from .context_snapshot import ContextSnapshot
from .context_validator import ContextValidator

__all__ = [
    "InstitutionContext",
    "WorkingContext",
    "MemoryContext",
    "ExecutionContext",
    "ExecutionGate",
    "GateResult",
    "ContextRuntime",
    "ContextSnapshot",
    "ContextValidator",
]
