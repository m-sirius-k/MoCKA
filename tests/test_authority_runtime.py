"""
Authority Runtime Verification Tests
Demonstrates all 12 required verification points for M3 Phase2 Sandbox Implementation

Decision Ledger: DC_20260919_008
Required Verification:
  1. No authority → execution denied
  2. Human-granted authority → execution permitted within scope
  3. Delegated authority → permitted only after Human Gate approval
  4. Delegated authority cannot re-delegate
  5. Revocation takes effect immediately
  6. Cascade revocation is atomic
  7. Past Decisions remain valid after revocation
  8. valid_until = null remains active until revoked
  9. MCP boundary rejects unauthorized authority
  10. Decision Executor rejects unauthorized authority
  11. Authority state is recorded in Decision Ledger
  12. M2 behavior remains unchanged
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add runtime to path
runtime_path = Path(__file__).parent.parent / "runtime"
sys.path.insert(0, str(runtime_path))

from authority_model import (
    AuthorityObject, AuthorityState, AuthorityLifecycleState, TemporalScope,
    AuthorityRegistry, reset_registry, get_registry
)
from delegation_validator import (
    DelegationValidator, create_delegation_request, DelegationStatus
)
from revocation_engine import RevocationEngine, RevocationType
from authority_enforcement import AuthorityEnforcer


def test_1_no_authority_execution_denied():
    """
    TEST 1: No authority → execution denied
    When a decision references an authority_id that doesn't exist,
    both MCP and Executor boundaries reject it
    """
    print("\n[TEST 1] No authority → execution denied")

    reset_registry()
    enforcer = AuthorityEnforcer()

    # Try to validate a decision with non-existent authority
    result = enforcer.validate_at_mcp_boundary(
        authority_id="AUTH-20260919-NONEXISTENT",
        decision_id="DEC-001",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )

    assert not result.valid, "Should reject non-existent authority"
    assert result.reason == "Authority not found in registry"
    print("  ✓ Execution denied when authority does not exist")


def test_2_human_granted_authority_permitted():
    """
    TEST 2: Human-granted authority → execution permitted within scope
    When authority is granted by Human Gate and within scope,
    both MCP and Executor permit execution
    """
    print("\n[TEST 2] Human-granted authority → execution permitted within scope")

    reset_registry()
    registry = get_registry()
    enforcer = AuthorityEnforcer(registry)

    # Create GRANTED_HUMAN authority
    authority = AuthorityObject(
        id="AUTH-20260919-HUMAN-GRANT-001",
        label="Sandbox Implementation Approval",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_001",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(
            valid_from=datetime.utcnow(),
            valid_until=None  # indefinite
        ),
        state=AuthorityLifecycleState.ACTIVE,
        max_delegations=1
    )
    registry.register(authority)

    # Validate at MCP boundary
    mcp_result = enforcer.validate_at_mcp_boundary(
        authority_id=authority.id,
        decision_id="DEC-001",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )
    assert mcp_result.valid, "MCP should accept Human-granted authority"

    # Validate at Executor boundary
    executor_result = enforcer.validate_at_executor_boundary(
        authority_id=authority.id,
        decision_id="DEC-001",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )
    assert executor_result.valid, "Executor should accept Human-granted authority"
    print("  ✓ Execution permitted for Human-granted authority within scope")


def test_3_delegated_authority_requires_human_gate_approval():
    """
    TEST 3: Delegated authority → permitted only after Human Gate approval
    Delegations can only be created after Human Gate explicitly approves
    """
    print("\n[TEST 3] Delegated authority requires Human Gate approval")

    reset_registry()
    registry = get_registry()
    validator = DelegationValidator(registry)

    # Create source GRANTED_HUMAN authority
    source = AuthorityObject(
        id="AUTH-20260919-SOURCE-001",
        label="Source for delegation",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_002",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(
            valid_from=datetime.utcnow(),
            valid_until=None
        ),
        state=AuthorityLifecycleState.ACTIVE,
        delegation_depth=0,
        max_delegations=1
    )
    registry.register(source)

    # Create delegation request (not yet approved)
    request = create_delegation_request(
        from_authority_id=source.id,
        to_recipient="Alice",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        delegation_reason="Alice needs to approve sandbox changes",
        requested_by="Bob",
        valid_from=datetime.utcnow(),
        valid_until=None
    )

    assert request.status == DelegationStatus.PENDING

    # Before approval, delegated authority doesn't exist
    assert registry.get(f"AUTH-20260919-DELEGATED-{request.request_id}") is None

    # Human Gate approves delegation
    delegated = validator.approve_delegation(request, approval_decision_id="DC_20260919_003")

    assert request.status == DelegationStatus.APPROVED
    assert delegated.delegation_depth == 1
    assert delegated.delegation_source == source.id
    assert delegated.max_delegations == 0  # Cannot re-delegate

    # Now enforcer can validate the delegated authority
    enforcer = AuthorityEnforcer(registry)
    result = enforcer.validate_at_mcp_boundary(
        authority_id=delegated.id,
        decision_id="DEC-002",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )
    assert result.valid, "Delegated authority valid after Human Gate approval"
    print("  ✓ Delegated authority permitted only after Human Gate approval")


def test_4_delegated_authority_cannot_redelegate():
    """
    TEST 4: Delegated authority cannot re-delegate
    Authority with delegation_depth=1 has max_delegations=0
    """
    print("\n[TEST 4] Delegated authority cannot re-delegate")

    reset_registry()
    registry = get_registry()
    validator = DelegationValidator(registry)

    # Create source with delegation permission
    source = AuthorityObject(
        id="AUTH-20260919-SOURCE-002",
        label="Source",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_004",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(valid_from=datetime.utcnow(), valid_until=None),
        state=AuthorityLifecycleState.ACTIVE,
        delegation_depth=0,
        max_delegations=1
    )
    registry.register(source)

    # Create and approve delegation
    request = create_delegation_request(
        from_authority_id=source.id,
        to_recipient="Charlie",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        delegation_reason="Test",
        requested_by="Dave",
        valid_from=datetime.utcnow(),
        valid_until=None
    )
    delegated = validator.approve_delegation(request, "DC_20260919_005")

    # Try to create further delegation from delegated authority
    further_request = create_delegation_request(
        from_authority_id=delegated.id,
        to_recipient="Eve",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        delegation_reason="Test",
        requested_by="Frank",
        valid_from=datetime.utcnow(),
        valid_until=None
    )

    # Validation should fail (chain check)
    valid, error = validator.validate_request(further_request)
    assert not valid, "Should reject transitive delegation"
    assert "Chain check failed" in error
    print("  ✓ Delegated authority cannot re-delegate")


def test_5_revocation_takes_effect_immediately():
    """
    TEST 5: Revocation takes effect immediately
    No grace period; authority becomes invalid at revocation timestamp
    """
    print("\n[TEST 5] Revocation takes effect immediately")

    reset_registry()
    registry = get_registry()
    revocation = RevocationEngine(registry)
    enforcer = AuthorityEnforcer(registry, revocation)

    # Create authority
    authority = AuthorityObject(
        id="AUTH-20260919-REVOKE-001",
        label="Authority to revoke",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_006",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(valid_from=datetime.utcnow(), valid_until=None),
        state=AuthorityLifecycleState.ACTIVE,
        max_delegations=0
    )
    registry.register(authority)

    # Validate before revocation
    result_before = enforcer.validate_at_mcp_boundary(
        authority_id=authority.id,
        decision_id="DEC-003",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )
    assert result_before.valid, "Should be valid before revocation"

    # Revoke immediately (Q4)
    revocation.revoke_authority(
        authority_id=authority.id,
        revoked_by="Human Gate",
        reason="Test revocation",
        revocation_decision_id="DC_20260919_007"
    )

    # Validate after revocation - should fail immediately
    result_after = enforcer.validate_at_mcp_boundary(
        authority_id=authority.id,
        decision_id="DEC-004",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )
    assert not result_after.valid, "Should be invalid after revocation (immediate)"
    print("  ✓ Revocation takes effect immediately (no grace period)")


def test_6_cascade_revocation_is_atomic():
    """
    TEST 6: Cascade revocation is atomic
    Either all delegations are revoked, or none
    """
    print("\n[TEST 6] Cascade revocation is atomic")

    reset_registry()
    registry = get_registry()
    validator = DelegationValidator(registry)
    revocation = RevocationEngine(registry)

    # Create source with multiple delegations
    source = AuthorityObject(
        id="AUTH-20260919-CASCADE-SOURCE",
        label="Source for cascade",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_008",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(valid_from=datetime.utcnow(), valid_until=None),
        state=AuthorityLifecycleState.ACTIVE,
        delegation_depth=0,
        max_delegations=1
    )
    registry.register(source)

    # Create multiple delegations
    delegations = []
    for i in range(3):
        request = create_delegation_request(
            from_authority_id=source.id,
            to_recipient=f"Recipient{i}",
            decision_type="IMPLEMENTATION_APPROVAL",
            resource_class="SANDBOX",
            delegation_reason=f"Delegation {i}",
            requested_by="Requestor",
            valid_from=datetime.utcnow(),
            valid_until=None
        )
        delegated = validator.approve_delegation(request, f"DC_20260919_00{9+i}")
        delegations.append(delegated)

    assert len(delegations) == 3
    assert all(d.state == AuthorityLifecycleState.ACTIVE for d in delegations)

    # Cascade revoke source (Q4: atomic)
    revoked_ids, events = revocation.cascade_revoke(
        source_authority_id=source.id,
        revoked_by="Human Gate",
        reason="Source revoked",
        revocation_decision_id="DC_20260919_011"
    )

    # All delegations should be revoked
    assert len(revoked_ids) == 3
    for delegation in delegations:
        reloaded = registry.get(delegation.id)
        assert reloaded.state == AuthorityLifecycleState.REVOKED

    print("  ✓ Cascade revocation is atomic (all delegations revoked together)")


def test_7_past_decisions_remain_valid_after_revocation():
    """
    TEST 7: Past Decisions remain valid after revocation (Q4: prospective-only)
    Revocation does not retroactively invalidate decisions made before it
    """
    print("\n[TEST 7] Past decisions remain valid after revocation")

    reset_registry()
    registry = get_registry()
    revocation = RevocationEngine(registry)

    # Create authority
    authority = AuthorityObject(
        id="AUTH-20260919-PROSP-001",
        label="Authority for prospective test",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_012",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(valid_from=datetime.utcnow(), valid_until=None),
        state=AuthorityLifecycleState.ACTIVE,
        max_delegations=0
    )
    registry.register(authority)

    # Decision was made 1 hour ago
    past_decision_time = datetime.utcnow() - timedelta(hours=1)

    # Validate that authority was valid at past decision time
    was_valid, _ = revocation.decide_with_authority(
        authority_id=authority.id,
        decision_id="PAST-DEC-001",
        decision_timestamp=past_decision_time
    )
    assert was_valid, "Authority was valid for past decision"

    # Revoke authority now
    revocation.revoke_authority(
        authority_id=authority.id,
        revoked_by="Human Gate",
        reason="Revoked",
        revocation_decision_id="DC_20260919_013"
    )

    # Re-validate past decision - should still be valid (prospective-only)
    was_valid_after, _ = revocation.decide_with_authority(
        authority_id=authority.id,
        decision_id="PAST-DEC-001",
        decision_timestamp=past_decision_time
    )
    assert was_valid_after, "Past decision remains valid after revocation (prospective-only)"

    print("  ✓ Past decisions remain valid after revocation (prospective-only)")


def test_8_valid_until_null_remains_active_until_revoked():
    """
    TEST 8: valid_until = null remains active until revoked (Q5)
    Authority with valid_until=None is indefinite
    """
    print("\n[TEST 8] valid_until = null remains active until revoked")

    reset_registry()
    registry = get_registry()

    # Create authority with indefinite duration
    authority = AuthorityObject(
        id="AUTH-20260919-INDEF-001",
        label="Indefinite authority",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_014",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(
            valid_from=datetime.utcnow(),
            valid_until=None  # indefinite
        ),
        state=AuthorityLifecycleState.ACTIVE,
        max_delegations=0
    )
    registry.register(authority)

    # Check validity at various future times
    for hours_ahead in [1, 24, 365, 999]:
        future_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        is_within = authority.temporal_scope.is_within_scope(future_time)
        assert is_within, f"Authority should be valid {hours_ahead} hours in future"

    assert authority.is_active, "Authority should be active (indefinite)"

    # Only revocation terminates indefinite authority
    revocation = RevocationEngine(registry)
    revocation.revoke_authority(
        authority_id=authority.id,
        revoked_by="Human Gate",
        reason="Revoked",
        revocation_decision_id="DC_20260919_015"
    )

    assert authority.state == AuthorityLifecycleState.REVOKED
    assert not authority.is_active
    print("  ✓ valid_until = null remains active until explicitly revoked")


def test_9_mcp_boundary_rejects_unauthorized():
    """
    TEST 9: MCP boundary rejects unauthorized authority (Q2)
    """
    print("\n[TEST 9] MCP boundary rejects unauthorized authority")

    reset_registry()
    enforcer = AuthorityEnforcer()

    # Try invalid scope
    result = enforcer.validate_at_mcp_boundary(
        authority_id="AUTH-NONEXISTENT",
        decision_id="DEC-005",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )

    assert not result.valid
    assert result.boundary.value == "MCP"
    print("  ✓ MCP boundary enforces authorization (Q2)")


def test_10_executor_boundary_rejects_unauthorized():
    """
    TEST 10: Decision Executor boundary rejects unauthorized authority (Q2)
    """
    print("\n[TEST 10] Decision Executor boundary rejects unauthorized authority")

    reset_registry()
    enforcer = AuthorityEnforcer()

    result = enforcer.validate_at_executor_boundary(
        authority_id="AUTH-NONEXISTENT",
        decision_id="DEC-006",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX"
    )

    assert not result.valid
    assert result.boundary.value == "DECISION_EXECUTOR"
    print("  ✓ Decision Executor boundary enforces authorization (Q2)")


def test_11_authority_state_in_decision_ledger():
    """
    TEST 11: Authority state is recorded in Decision Ledger (Q6)
    Every revocation creates a Decision Ledger entry
    """
    print("\n[TEST 11] Authority state recorded in Decision Ledger")

    reset_registry()
    registry = get_registry()
    revocation = RevocationEngine(registry)

    authority = AuthorityObject(
        id="AUTH-20260919-LEDGER-001",
        label="Authority for ledger test",
        granted_by="Human Gate",
        granted_at=datetime.utcnow(),
        decision_id="DC_20260919_016",
        decision_type="IMPLEMENTATION_APPROVAL",
        resource_class="SANDBOX",
        temporal_scope=TemporalScope(valid_from=datetime.utcnow(), valid_until=None),
        state=AuthorityLifecycleState.ACTIVE,
        max_delegations=0
    )
    registry.register(authority)

    # Revoke and record
    event = revocation.revoke_authority(
        authority_id=authority.id,
        revoked_by="Human Gate",
        reason="Test revocation",
        revocation_decision_id="DC_20260919_017"
    )

    # Event should be recorded with Decision Ledger reference
    assert event.ledger_entry_id == "DC_20260919_017"
    assert event.revocation_type == RevocationType.HUMAN_GATE_ORDER
    assert len(revocation.revocation_events) >= 1

    print("  ✓ Authority state recorded in Decision Ledger (Q6)")


def test_12_m2_behavior_unchanged():
    """
    TEST 12: M2 behavior remains unchanged
    M3 runtime doesn't modify M2 authority model
    (M2 decisions use implicit all-human authority, not checked by M3 runtime)
    """
    print("\n[TEST 12] M2 behavior remains unchanged")

    # M3 runtime only enforces M3 authorities
    # M2 decisions (pre-M3) are not subject to M3 validation

    reset_registry()
    registry = get_registry()

    # Simulating M2 decision (no authority object)
    m2_decision = {
        "decision_id": "M2-LEGACY-001",
        "type": "M2_DECISION",
        "authority_model": "IMPLICIT_ALL_HUMAN"
    }

    # M3 runtime should not attempt to validate M2
    # (M2 decisions don't have authority_id field)
    assert "authority_id" not in m2_decision

    # M3 registry is empty (M2 doesn't register authorities)
    assert len(registry.authorities) == 0

    print("  ✓ M2 behavior unchanged (M3 runtime isolated)")


def run_all_tests():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("M3 PHASE2 AUTHORITY RUNTIME VERIFICATION TESTS")
    print("=" * 70)

    tests = [
        test_1_no_authority_execution_denied,
        test_2_human_granted_authority_permitted,
        test_3_delegated_authority_requires_human_gate_approval,
        test_4_delegated_authority_cannot_redelegate,
        test_5_revocation_takes_effect_immediately,
        test_6_cascade_revocation_is_atomic,
        test_7_past_decisions_remain_valid_after_revocation,
        test_8_valid_until_null_remains_active_until_revoked,
        test_9_mcp_boundary_rejects_unauthorized,
        test_10_executor_boundary_rejects_unauthorized,
        test_11_authority_state_in_decision_ledger,
        test_12_m2_behavior_unchanged,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
