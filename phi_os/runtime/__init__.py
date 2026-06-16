# phi_os/runtime/__init__.py
# Institution Runtime パッケージ公開API
from .institution_runtime import InstitutionRuntime
from .runtime_types import (
    Artifact, Meaning, Institution, Authority, Gate,
    BindingResult, ComplianceResult, ComplianceViolation, EventContext,
    BindingStatus, MeaningClass, AuthorityType, GateId, GateStatus,
    ViolationSeverity,
)
from .runtime_errors import (
    InstitutionRuntimeError, BindingError, AuthorityConflictError,
    MeaningNotFoundError, GateValidationError, InstitutionResolutionError,
    ComplianceViolationError, OrphanArtifactError, ShadowArtifactError,
    DuplicateBindingError,
)

__all__ = [
    "InstitutionRuntime",
    "Artifact", "Meaning", "Institution", "Authority", "Gate",
    "BindingResult", "ComplianceResult", "ComplianceViolation", "EventContext",
    "BindingStatus", "MeaningClass", "AuthorityType", "GateId", "GateStatus",
    "ViolationSeverity",
    "InstitutionRuntimeError", "BindingError", "AuthorityConflictError",
    "MeaningNotFoundError", "GateValidationError", "InstitutionResolutionError",
    "ComplianceViolationError", "OrphanArtifactError", "ShadowArtifactError",
    "DuplicateBindingError",
]
