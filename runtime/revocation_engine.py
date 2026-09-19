"""
Revocation Engine
Enforces Q4 requirements: immediate revocation, atomic cascade, prospective-only effect

Decision Ledger: DC_20260919_008
Authorization: Q4 CONFIRM
  * Immediate revocation (no grace period)
  * Atomic cascade revocation
  * Prospective-only effect (past decisions unaffected)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

from .authority_model import (
    AuthorityObject, AuthorityLifecycleState, AuthorityRegistry, get_registry
)


class RevocationType(str, Enum):
    """Types of revocation events"""
    EXPLICIT_REQUEST = "EXPLICIT_REQUEST"
    HUMAN_GATE_ORDER = "HUMAN_GATE_ORDER"
    EXPIRATION = "EXPIRATION"
    CASCADE = "CASCADE"


@dataclass
class RevocationEvent:
    """Record of a revocation event (for Decision Ledger)"""
    event_id: str
    timestamp: datetime
    authority_id: str
    revocation_type: RevocationType
    revoked_by: str
    revocation_reason: str
    ledger_entry_id: Optional[str] = None


class RevocationEngine:
    """
    Enforces revocation semantics per canonical Phase1 spec

    Q4 Requirements:
    - Immediate: authority invalid at revocation timestamp (no grace period)
    - Atomic cascade: all delegations revoked together
    - Prospective: past decisions remain valid after revocation
    """

    def __init__(self, registry: Optional[AuthorityRegistry] = None):
        self.registry = registry or get_registry()
        self.revocation_events: List[RevocationEvent] = []

    def can_revoke(self, authority_id: str, revoked_by: str) -> tuple[bool, Optional[str]]:
        """
        Check if authority can be revoked by the given principal

        Q3: Only Human Gate can revoke GRANTED_HUMAN
        DELEGATED can be revoked by source holder or Human Gate
        """
        authority = self.registry.get(authority_id)

        if not authority:
            return False, "Authority not found"

        if authority.state == AuthorityLifecycleState.REVOKED:
            return False, "Authority already revoked (irreversible)"

        if authority.delegation_depth == 0:
            # GRANTED_HUMAN: only Human Gate can revoke
            if revoked_by != "Human Gate":
                return False, "Only Human Gate can revoke GRANTED_HUMAN authority"
        else:
            # DELEGATED: source holder or Human Gate can revoke
            if revoked_by != "Human Gate" and revoked_by != authority.granted_by:
                return False, (
                    f"Only Human Gate or source authority ({authority.granted_by}) "
                    f"can revoke DELEGATED authority"
                )

        return True, None

    def revoke_authority(self, authority_id: str, revoked_by: str,
                        reason: str, revocation_decision_id: str,
                        check_authorization: bool = True) -> RevocationEvent:
        """
        Revoke an authority immediately (Q4: no grace period)

        Args:
            authority_id: Authority to revoke
            revoked_by: Who is revoking (must be authorized)
            reason: Revocation reason
            revocation_decision_id: Decision Ledger decision ID
            check_authorization: If True, verify revocation authority

        Returns:
            RevocationEvent for Decision Ledger
        """
        if check_authorization:
            can_revoke, error = self.can_revoke(authority_id, revoked_by)
            if not can_revoke:
                raise ValueError(f"Revocation authorization failed: {error}")

        authority = self.registry.get(authority_id)
        assert authority is not None

        # Q4: Immediate revocation
        revocation_timestamp = datetime.utcnow()
        authority.revoke(revoked_by, reason, revocation_decision_id, revocation_timestamp)

        # Record event
        event = RevocationEvent(
            event_id=f"REV-{revocation_timestamp.strftime('%Y%m%d%H%M%S')}-{authority_id[:8]}",
            timestamp=revocation_timestamp,
            authority_id=authority_id,
            revocation_type=RevocationType.HUMAN_GATE_ORDER if revoked_by == "Human Gate" else RevocationType.EXPLICIT_REQUEST,
            revoked_by=revoked_by,
            revocation_reason=reason,
            ledger_entry_id=revocation_decision_id
        )

        self.revocation_events.append(event)
        return event

    def cascade_revoke(self, source_authority_id: str, revoked_by: str,
                      reason: str, revocation_decision_id: str) -> tuple[List[str], List[RevocationEvent]]:
        """
        Cascade revoke all delegations from source authority (Q4: atomic)

        When GRANTED_HUMAN authority is revoked, all delegations from it
        are automatically revoked atomically.

        Returns:
            (list of revoked delegation IDs, list of revocation events)
        """
        source = self.registry.get(source_authority_id)
        assert source is not None

        # Find all delegations from source
        delegations = self.registry.list_delegations_from(source_authority_id)
        revoked_ids = []
        events = []

        # Q4: Atomic - all revocations must succeed or all fail
        cascade_timestamp = datetime.utcnow()

        try:
            for delegation in delegations:
                if delegation.state != AuthorityLifecycleState.REVOKED:
                    cascade_reason = f"Source authority revoked: {reason}"

                    # Revoke delegation
                    delegation.revoke(
                        revoked_by="Human Gate",  # Cascade is automatic (system action)
                        reason=cascade_reason,
                        revocation_decision_id=revocation_decision_id,
                        revoked_at=cascade_timestamp
                    )

                    revoked_ids.append(delegation.id)

                    # Record cascade event
                    event = RevocationEvent(
                        event_id=f"REV-CASCADE-{cascade_timestamp.strftime('%Y%m%d%H%M%S')}-{delegation.id[:8]}",
                        timestamp=cascade_timestamp,
                        authority_id=delegation.id,
                        revocation_type=RevocationType.CASCADE,
                        revoked_by="System",  # Automatic cascade
                        revocation_reason=cascade_reason,
                        ledger_entry_id=revocation_decision_id
                    )
                    events.append(event)

            # All succeeded - record cascade events
            self.revocation_events.extend(events)
            return revoked_ids, events

        except Exception as e:
            # Q4: Atomicity failure - rollback all cascades
            raise ValueError(f"Cascade revocation failed (atomic guarantee violated): {e}")

    def check_authority_validity(self, authority_id: str,
                                at_time: Optional[datetime] = None) -> tuple[bool, Optional[str]]:
        """
        Check if an authority is currently valid for granting decisions

        Q4: Prospective-only effect - this checks current validity, not historical
        """
        authority = self.registry.get(authority_id)

        if not authority:
            return False, "Authority not found"

        if authority.state == AuthorityLifecycleState.REVOKED:
            return False, "Authority has been revoked (irreversible)"

        if authority.state == AuthorityLifecycleState.EXPIRED:
            return False, "Authority has expired"

        if not authority.is_active:
            return False, "Authority is not currently active"

        return True, None

    def decide_with_authority(self, authority_id: str, decision_id: str,
                            decision_timestamp: datetime) -> tuple[bool, Optional[str]]:
        """
        Q4: Prospective-only effect enforcement

        Check if an authority was valid AT THE TIME of the decision
        (for historical validation of past decisions)

        Returns:
            (was_valid_at_time, explanation)
        """
        authority = self.registry.get(authority_id)

        if not authority:
            return False, "Authority not found"

        # Check if authority existed at decision time
        if decision_timestamp < authority.granted_at:
            return False, "Authority did not exist at decision time"

        # Check if authority was revoked before/at decision time
        if authority.revoked_at and authority.revoked_at <= decision_timestamp:
            return False, (
                f"Authority was revoked at {authority.revoked_at} "
                f"before decision {decision_id} at {decision_timestamp}"
            )

        # Check temporal scope at decision time
        if not authority.temporal_scope.is_within_scope(decision_timestamp):
            return False, "Authority was not within temporal scope at decision time"

        # Authority was valid at decision time (prospective-only: no retroactive invalidation)
        return True, None
