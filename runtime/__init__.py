"""
M3 Phase 2 Authority Runtime
Canonical Authority Model Materialization (Sandbox)

Exports: Authority model, delegation validator, revocation engine, enforcement
"""

from .authority_model import (
    AuthorityState,
    AuthorityLifecycleState,
    TemporalScope,
    AuthorityObject,
    AuthorityRegistry,
    get_registry,
    reset_registry,
)

from .delegation_validator import (
    DelegationValidator,
    DelegationRequest,
    DelegationStatus,
    create_delegation_request,
    DelegationValidationError,
)

from .revocation_engine import (
    RevocationEngine,
    RevocationEvent,
    RevocationType,
)

from .authority_enforcement import (
    AuthorityEnforcer,
    AuthorityValidationResult,
    EnforcementBoundary,
    validate_authority_exists,
    validate_authority_is_active,
    validate_authority_scope,
)

__all__ = [
    "AuthorityState",
    "AuthorityLifecycleState",
    "TemporalScope",
    "AuthorityObject",
    "AuthorityRegistry",
    "get_registry",
    "reset_registry",
    "DelegationValidator",
    "DelegationRequest",
    "DelegationStatus",
    "create_delegation_request",
    "DelegationValidationError",
    "RevocationEngine",
    "RevocationEvent",
    "RevocationType",
    "AuthorityEnforcer",
    "AuthorityValidationResult",
    "EnforcementBoundary",
    "validate_authority_exists",
    "validate_authority_is_active",
    "validate_authority_scope",
]
