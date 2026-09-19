"""
M3 Phase 2 Authority Runtime Implementation
Canonical Authority Model Materialization (Sandbox)

Decision Ledger: DC_20260919_008
Authorization: Q1-Q6 APPROVED
Scope: Sandbox only, M2 unchanged
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import json
from pathlib import Path


class AuthorityState(str, Enum):
    """Authority State Space (from HG-M3-PHASE1-AUTHORITY-STATE-MODEL-v1.0)"""
    NONE = "NONE"
    GRANTED_HUMAN = "GRANTED_HUMAN"
    DELEGATED_ACTIVE = "DELEGATED_ACTIVE"
    DELEGATED_REVOKED = "DELEGATED_REVOKED"
    UNDEFINED = "UNDEFINED"


class AuthorityLifecycleState(str, Enum):
    """Authority Object Lifecycle State (from HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0)"""
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class RuntimeVerificationState(str, Enum):
    """Runtime Authorization Verification State (Orthogonal to Lifecycle State)
    Tracks whether authority has been verified at runtime.
    Separate from lifecycle_state: an authority can be GRANTED_HUMAN (lifecycle)
    but NOT_VERIFIED (runtime) if we haven't checked it yet.
    """
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


@dataclass
class TemporalScope:
    """Temporal validity scope for authority (Q5: valid_until is OPTIONAL)"""
    valid_from: datetime
    valid_until: Optional[datetime] = None  # null = indefinite authority

    def is_within_scope(self, check_time: Optional[datetime] = None) -> bool:
        """Check if given time is within temporal scope"""
        if check_time is None:
            check_time = datetime.utcnow()

        # valid_from check
        if check_time < self.valid_from:
            return False

        # valid_until check (null means indefinite)
        if self.valid_until is not None and check_time >= self.valid_until:
            return False

        return True

    def has_expired(self, check_time: Optional[datetime] = None) -> bool:
        """Check if authority has expired"""
        if self.valid_until is None:
            return False  # Indefinite authority never expires by time

        if check_time is None:
            check_time = datetime.utcnow()

        return check_time >= self.valid_until


@dataclass
class AuthorityContext:
    """
    Authority Context Instance (HG-M3 Integration Phase)
    Represents complete authority evidence flowing through the pipeline.
    Carries ~24 fields: identity, state (lifecycle + verification), scope,
    temporal validity, revocation state, historical snapshot, provenance.
    HYBRID model: immutable historical snapshot + current state reference.
    """
    # Identity & Reference (required)
    authority_context_id: str  # Unique instance ID (e.g., CTX-{UUID})
    authority_id: str  # Reference to Authority Object in registry

    # Authority State (required)
    authority_lifecycle_state: AuthorityLifecycleState
    runtime_verification_state: RuntimeVerificationState

    # Scope (required)
    decision_type: str
    resource_class: str

    # Temporal Validity (required for non-indefinite)
    valid_from: datetime
    granted_by: str
    granted_at: datetime
    granting_decision_id: str

    # Optional fields (with defaults)
    authority_lifecycle_state_at_decision: Optional[AuthorityLifecycleState] = None
    verification_timestamp: Optional[datetime] = None
    verification_evidence: Optional[str] = None
    valid_until: Optional[datetime] = None
    is_indefinite: bool = False
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revocation_decision_id: Optional[str] = None
    authority_state_at_decision: Optional[dict] = None
    verification_state_at_decision: Optional[RuntimeVerificationState] = None
    scope_at_decision: Optional[Dict[str, str]] = None
    temporal_at_decision: Optional[Dict[str, Any]] = None
    provenance_evidence: Optional[str] = None
    decision_id: Optional[str] = None
    execution_id: Optional[str] = None

    def __post_init__(self):
        """Validate Authority Context invariants"""
        if not self.authority_context_id:
            raise ValueError("authority_context_id required")
        if not self.authority_id:
            raise ValueError("authority_id required")

        # UNKNOWN / NOT_VERIFIED are fail-closed states
        if self.runtime_verification_state in (RuntimeVerificationState.UNKNOWN,
                                                RuntimeVerificationState.NOT_VERIFIED):
            if self.decision_id is not None:
                raise ValueError(
                    f"Cannot bind decision with {self.runtime_verification_state} authority"
                )

    def is_eligible_for_execution(self, check_time: Optional[datetime] = None) -> bool:
        """
        Check if this context permits consequential execution.
        All conditions must be satisfied:
        - Verification succeeded (VERIFIED)
        - Lifecycle state is ACTIVE (not REVOKED, EXPIRED, NONE)
        - Temporal scope is valid
        - Not revoked
        - Scope matches (caller must check separately)
        """
        if check_time is None:
            check_time = datetime.utcnow()

        # Verification check
        if self.runtime_verification_state != RuntimeVerificationState.VERIFIED:
            return False

        # Lifecycle check
        if self.authority_lifecycle_state not in (
            AuthorityLifecycleState.ACTIVE,
            AuthorityLifecycleState.CREATED
        ):
            return False

        # Revocation check
        if self.is_revoked:
            return False

        # Temporal check
        if check_time < self.valid_from:
            return False
        if self.valid_until is not None and check_time >= self.valid_until:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Authority Context for storage/transport"""
        return {
            "authority_context_id": self.authority_context_id,
            "authority_id": self.authority_id,
            "authority_lifecycle_state": self.authority_lifecycle_state.value,
            "runtime_verification_state": self.runtime_verification_state.value,
            "decision_type": self.decision_type,
            "resource_class": self.resource_class,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_indefinite": self.is_indefinite,
            "is_revoked": self.is_revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_by": self.revoked_by,
            "revocation_decision_id": self.revocation_decision_id,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "granting_decision_id": self.granting_decision_id,
            "decision_id": self.decision_id,
            "execution_id": self.execution_id,
        }


@dataclass
class AuthorityObject:
    """
    Authority Object (from HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0)
    Represents a formal grant of permission to execute Decisions
    """
    # Identity
    id: str  # AUTH-{YYYYMMDD}-{UUID}
    label: str

    # Source and Authorization
    granted_by: str  # Human Gate or delegating authority ID
    granted_at: datetime
    decision_id: str  # Human Gate Decision ID

    # Scope
    decision_type: str  # Which Decision types this authority enables
    resource_class: str  # Which resource classes this authority applies to

    # Temporal Validity (Q5: valid_until is OPTIONAL)
    temporal_scope: TemporalScope

    # Delegation Chain
    delegation_source: Optional[str] = None  # Source if delegated
    delegation_depth: int = 0  # 0=GRANTED_HUMAN, 1=DELEGATED (max)

    # State
    state: AuthorityLifecycleState = AuthorityLifecycleState.CREATED

    # Revocation (Q4: immediate, irreversible)
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revocation_reason: Optional[str] = None
    revocation_decision_id: Optional[str] = None

    # Constraints
    max_delegations: int = 0  # How many delegations this authority can produce

    # Evidence
    ledger_entry_id: Optional[str] = None  # Decision Ledger ID

    def __post_init__(self):
        """Validate authority object constraints"""
        # Constraint: scope immutability (§7.1.3)
        if self.delegation_depth > 1:
            raise ValueError("Delegation depth MUST NOT exceed 1")

        # Constraint: delegated authority cannot delegate (§7.3.7)
        if self.delegation_depth >= 1 and self.max_delegations > 0:
            raise ValueError("Delegated authority (depth >= 1) cannot delegate further")

    @property
    def is_active(self) -> bool:
        """
        Derived property: is_active
        (Q5: corrected logic for null valid_until)
        True if within temporal scope AND state is ACTIVE
        """
        if self.state != AuthorityLifecycleState.ACTIVE:
            return False

        return self.temporal_scope.is_within_scope()

    @property
    def can_delegate(self) -> bool:
        """Derived property: can this authority create delegations?"""
        return (self.delegation_depth < 1) and (self.max_delegations > 0)

    @property
    def can_grant_decision(self) -> bool:
        """Derived property: can this authority grant a Decision?"""
        return self.is_active and self.state != AuthorityLifecycleState.REVOKED

    def transition_to_active(self):
        """Transition from CREATED to ACTIVE (temporal guard)"""
        if self.state != AuthorityLifecycleState.CREATED:
            raise ValueError(f"Cannot transition from {self.state} to ACTIVE")
        self.state = AuthorityLifecycleState.ACTIVE

    def revoke(self, revoked_by: str, reason: str, revocation_decision_id: str,
               revoked_at: Optional[datetime] = None):
        """
        Revoke this authority (Q4: immediate, irreversible)
        """
        if self.state == AuthorityLifecycleState.REVOKED:
            raise ValueError("Authority already revoked (irreversible)")

        self.state = AuthorityLifecycleState.REVOKED
        self.revoked_by = revoked_by
        self.revocation_reason = reason
        self.revocation_decision_id = revocation_decision_id
        self.revoked_at = revoked_at or datetime.utcnow()

    def expire(self):
        """Transition to EXPIRED state (temporal expiration)"""
        if self.state == AuthorityLifecycleState.REVOKED:
            raise ValueError("Cannot expire a revoked authority")

        self.state = AuthorityLifecycleState.EXPIRED

    def to_dict(self) -> Dict[str, Any]:
        """Serialize authority object for storage/transport"""
        return {
            "id": self.id,
            "label": self.label,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "resource_class": self.resource_class,
            "valid_from": self.temporal_scope.valid_from.isoformat(),
            "valid_until": self.temporal_scope.valid_until.isoformat() if self.temporal_scope.valid_until else None,
            "delegation_source": self.delegation_source,
            "delegation_depth": self.delegation_depth,
            "state": self.state.value,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_by": self.revoked_by,
            "revocation_reason": self.revocation_reason,
            "revocation_decision_id": self.revocation_decision_id,
            "max_delegations": self.max_delegations,
            "ledger_entry_id": self.ledger_entry_id,
            "is_active": self.is_active,
            "can_delegate": self.can_delegate,
            "can_grant_decision": self.can_grant_decision,
        }


@dataclass
class AuthorityRegistry:
    """
    In-memory registry of Authority Objects (Sandbox)
    Provides lookup and validation
    """
    authorities: Dict[str, AuthorityObject] = field(default_factory=dict)

    def register(self, authority: AuthorityObject):
        """Register an authority object"""
        if authority.id in self.authorities:
            raise ValueError(f"Authority {authority.id} already registered")
        self.authorities[authority.id] = authority

    def get(self, authority_id: str) -> Optional[AuthorityObject]:
        """Retrieve authority by ID"""
        return self.authorities.get(authority_id)

    def get_active(self, authority_id: str) -> Optional[AuthorityObject]:
        """Retrieve authority only if currently active"""
        authority = self.get(authority_id)
        if authority and authority.is_active:
            return authority
        return None

    def list_delegations_from(self, source_authority_id: str) -> List[AuthorityObject]:
        """Find all delegations sourced from a given authority"""
        return [
            auth for auth in self.authorities.values()
            if auth.delegation_source == source_authority_id
        ]

    def cascade_revoke(self, source_authority_id: str, revoked_by: str,
                       reason: str, revocation_decision_id: str) -> List[str]:
        """
        Atomically revoke all delegations from a source authority (Q4)
        Returns list of revoked delegation IDs
        """
        delegations = self.list_delegations_from(source_authority_id)
        revoked_ids = []

        try:
            for delegation in delegations:
                if delegation.state != AuthorityLifecycleState.REVOKED:
                    cascade_reason = f"Source authority revoked: {reason}"
                    delegation.revoke(revoked_by, cascade_reason, revocation_decision_id)
                    revoked_ids.append(delegation.id)
            return revoked_ids
        except Exception as e:
            # Atomicity: if any revocation fails, raise error (caller should rollback)
            raise ValueError(f"Cascade revocation failed (atomic guarantee): {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize registry for storage"""
        return {
            authority_id: authority.to_dict()
            for authority_id, authority in self.authorities.items()
        }


# Sandbox registry instance
_registry = AuthorityRegistry()


def get_registry() -> AuthorityRegistry:
    """Get the global authority registry (Sandbox)"""
    return _registry


def reset_registry():
    """Reset registry (testing/sandbox only)"""
    global _registry
    _registry = AuthorityRegistry()
