"""
Delegation Validator
Enforces single-level delegation, Human Gate approval requirement (Q3)

Decision Ledger: DC_20260919_008
Authorization: Q3 CONFIRM - Human Gate only approves delegation
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum

from .authority_model import (
    AuthorityObject, AuthorityLifecycleState, TemporalScope,
    AuthorityRegistry, get_registry
)


class DelegationValidationError(Exception):
    """Raised when delegation validation fails"""
    pass


class DelegationStatus(str, Enum):
    """Status of a delegation request"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class DelegationRequest:
    """
    Delegation Request (from HG-M3-PHASE1-DELEGATION-GOVERNANCE-FRAMEWORK-v1.0)

    Q1 Decision B: Only Human Gate may approve delegation
    Q2 Decision C: Eliminate Evaluate step; HG approves or rejects directly
    """
    request_id: str
    from_authority_id: str  # Source GRANTED_HUMAN Authority Object
    to_recipient: str  # Named individual
    decision_type: str  # Must match source scope
    resource_class: str  # Must match source scope
    delegation_reason: str
    requested_at: datetime
    requested_by: str
    valid_from: datetime
    valid_until: Optional[datetime]  # null = indefinite

    # Approval tracking (Q3: Human Gate only)
    approved_by: Optional[str] = None  # Must be "Human Gate"
    approved_at: Optional[datetime] = None
    status: DelegationStatus = DelegationStatus.PENDING
    approval_decision_id: Optional[str] = None
    rejection_reason: Optional[str] = None


class DelegationValidator:
    """
    Validates delegation requests and enforces canonical Phase1 rules

    Q1: Human Gate only
    Q2: Direct approval (no separate evaluation phase)
    Q3: Explicit Human Gate approval required
    """

    def __init__(self, registry: Optional[AuthorityRegistry] = None):
        self.registry = registry or get_registry()

    def validate_permission(self, source_authority_id: str) -> Tuple[bool, Optional[str]]:
        """
        Permission Check (from Framework §4.2)
        Validate source authority can delegate
        """
        source = self.registry.get(source_authority_id)

        if not source:
            return False, "Source authority not found"

        if source.delegation_depth > 0:
            return False, "Source authority is DELEGATED (depth > 0); cannot delegate further"

        if source.max_delegations <= 0:
            return False, "Source authority max_delegations = 0; delegation forbidden"

        if source.state != AuthorityLifecycleState.ACTIVE:
            return False, f"Source authority state is {source.state}; must be ACTIVE"

        return True, None

    def validate_scope(self, request: DelegationRequest) -> Tuple[bool, Optional[str]]:
        """
        Scope Check (from Framework §4.2)
        Validate delegated scope matches source scope
        """
        source = self.registry.get(request.from_authority_id)

        if not source:
            return False, "Source authority not found"

        # Delegated scope MUST match source scope (§6.1)
        if request.decision_type != source.decision_type:
            return False, (
                f"Delegated decision_type '{request.decision_type}' "
                f"does not match source '{source.decision_type}'"
            )

        if request.resource_class != source.resource_class:
            return False, (
                f"Delegated resource_class '{request.resource_class}' "
                f"does not match source '{source.resource_class}'"
            )

        return True, None

    def validate_temporal(self, request: DelegationRequest) -> Tuple[bool, Optional[str]]:
        """
        Temporal Check (from Framework §4.2)
        Validate temporal scope alignment
        """
        source = self.registry.get(request.from_authority_id)

        if not source:
            return False, "Source authority not found"

        # valid_from <= valid_until check
        if request.valid_until and request.valid_from >= request.valid_until:
            return False, "Delegation: valid_from >= valid_until"

        # Delegated scope must not extend beyond source scope
        if source.temporal_scope.valid_until and request.valid_until:
            if request.valid_until > source.temporal_scope.valid_until:
                return False, (
                    f"Delegated valid_until {request.valid_until} "
                    f"exceeds source valid_until {source.temporal_scope.valid_until}"
                )

        return True, None

    def validate_chain(self, request: DelegationRequest) -> Tuple[bool, Optional[str]]:
        """
        Chain Check (from Framework §4.2)
        Ensure resulting delegation depth is exactly 1 (no transitive)
        """
        source = self.registry.get(request.from_authority_id)

        if not source:
            return False, "Source authority not found"

        # Resulting delegation must be depth exactly 1
        resulting_depth = source.delegation_depth + 1

        if resulting_depth > 1:
            return False, (
                f"Resulting delegation depth {resulting_depth} exceeds maximum 1"
            )

        return True, None

    def validate_request(self, request: DelegationRequest) -> Tuple[bool, Optional[str]]:
        """
        Full validation of delegation request (Framework §4.2 criteria)
        Evaluates all criteria without separate Evaluation phase (Q2)
        """
        # Permission Check
        valid, error = self.validate_permission(request.from_authority_id)
        if not valid:
            return False, f"Permission check failed: {error}"

        # Scope Check
        valid, error = self.validate_scope(request)
        if not valid:
            return False, f"Scope check failed: {error}"

        # Temporal Check
        valid, error = self.validate_temporal(request)
        if not valid:
            return False, f"Temporal check failed: {error}"

        # Chain Check
        valid, error = self.validate_chain(request)
        if not valid:
            return False, f"Chain check failed: {error}"

        return True, None

    def approve_delegation(self, request: DelegationRequest,
                          approval_decision_id: str) -> AuthorityObject:
        """
        Approve delegation and create DELEGATED Authority Object

        Q3: Only Human Gate can call this (authorization boundary)
        Returns the created DELEGATED Authority Object
        """
        # Validate request before approval
        valid, error = self.validate_request(request)
        if not valid:
            raise DelegationValidationError(f"Cannot approve: {error}")

        source = self.registry.get(request.from_authority_id)
        assert source is not None  # Guaranteed by validation

        # Create DELEGATED Authority Object (Framework §4.3)
        delegated = AuthorityObject(
            id=f"AUTH-{datetime.utcnow().strftime('%Y%m%d')}-DELEGATED-{request.request_id}",
            label=f"Delegation to {request.to_recipient}",
            granted_by=request.from_authority_id,
            granted_at=datetime.utcnow(),
            decision_id=approval_decision_id,
            decision_type=request.decision_type,
            resource_class=request.resource_class,
            temporal_scope=TemporalScope(
                valid_from=request.valid_from,
                valid_until=request.valid_until  # null = indefinite
            ),
            delegation_source=request.from_authority_id,
            delegation_depth=1,  # Delegated authority
            state=AuthorityLifecycleState.CREATED,
            max_delegations=0,  # Delegated cannot delegate further
        )

        # Register the delegated authority
        self.registry.register(delegated)

        # Update request status
        request.status = DelegationStatus.APPROVED
        request.approved_by = "Human Gate"  # Q3: Only Human Gate can approve
        request.approved_at = datetime.utcnow()
        request.approval_decision_id = approval_decision_id

        return delegated

    def reject_delegation(self, request: DelegationRequest, reason: str):
        """Reject delegation request"""
        request.status = DelegationStatus.REJECTED
        request.rejection_reason = reason


def create_delegation_request(
    from_authority_id: str,
    to_recipient: str,
    decision_type: str,
    resource_class: str,
    delegation_reason: str,
    requested_by: str,
    valid_from: datetime,
    valid_until: Optional[datetime] = None
) -> DelegationRequest:
    """Factory to create a delegation request"""
    import uuid
    request_id = f"DEL-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    return DelegationRequest(
        request_id=request_id,
        from_authority_id=from_authority_id,
        to_recipient=to_recipient,
        decision_type=decision_type,
        resource_class=resource_class,
        delegation_reason=delegation_reason,
        requested_at=datetime.utcnow(),
        requested_by=requested_by,
        valid_from=valid_from,
        valid_until=valid_until
    )
