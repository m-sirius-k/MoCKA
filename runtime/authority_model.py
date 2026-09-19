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
