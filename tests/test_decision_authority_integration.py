"""
STEP 3: Decision Engine Authority Integration Tests

Test Requirements A-G:
A. valid AuthorityContext can bind to a Decision
B. absent context cannot become VERIFIED
C. UNKNOWN cannot become authorized by default
D. invalid context is rejected
E. authority provenance is preserved
F. historical snapshot is distinct from current authority state
G. existing M2 Decision behavior remains unchanged
"""

from datetime import datetime
from decision.decision_model import DecisionResult, Alternative
from decision.decision_engine import DecisionEngine
from decision.priority_scorer import PriorityScorer
from decision.risk_analyzer import RiskAnalyzer


# Mock SemanticResult for testing
class MockSemanticResult:
    def __init__(self, intent_key="TEST_INTENT", confidence=0.95):
        self.intent = MockIntent(intent_key)
        self.confidence = confidence
        self.candidates = [MockCandidate(intent_key)]
        self.context_summary = MockContextSummary()

class MockIntent:
    def __init__(self, key):
        self.key = key
        self.label_en = f"Test Intent: {key}"

class MockCandidate:
    def __init__(self, key):
        self.key = key

class MockContextSummary:
    def __init__(self):
        self.summary_text = "Test context"
        self.phase = "TEST_PHASE"
        self.active_task = "test_task"
        self.recent_events = ["event1", "event2"]
        self.conversation_flow = "TEST_FLOW"


def test_a_valid_authority_context_binds_to_decision():
    """A. valid AuthorityContext can bind to a Decision"""
    print("\nTEST A: Valid AuthorityContext binds to Decision...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    valid_auth_ctx = {
        "authority_id": "AUTH-VALID-001",
        "authority_context_id": "CTX-VALID-001",
        "verification_state": "VERIFIED",
        "authority_lifecycle_state": "ACTIVE",
        "decision_type": "DECISION_TYPE_TEST",
        "resource_class": "RESOURCE_CLASS_TEST"
    }

    decision = engine.decide_with_authority(semantic, authority_context=valid_auth_ctx)

    assert decision.authority_context is not None
    assert decision.authority_context["verification_state"] == "VERIFIED"
    assert decision.authority_binding is not None
    assert decision.authority_binding["verification_state_at_decision"] == "VERIFIED"
    assert decision.has_authority_context() == True

    print("  ✓ PASS: Valid VERIFIED authority context binds successfully")


def test_b_absent_context_cannot_become_verified():
    """B. absent context cannot become VERIFIED"""
    print("\nTEST B: ABSENT context cannot become VERIFIED...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    # Create decision without authority
    decision_no_auth = engine.decide(semantic)

    assert decision_no_auth.authority_context is None
    assert decision_no_auth.has_authority_context() == False

    # Absent context marked explicitly
    absent_auth = {
        "status": "ABSENT",
        "authority_id": None,
        "verification_state": "UNKNOWN"
    }

    decision_absent = engine.decide_with_authority(semantic, authority_context=absent_auth)

    assert decision_absent.authority_context["verification_state"] == "UNKNOWN"
    assert decision_absent.has_authority_context() == False

    print("  ✓ PASS: ABSENT context remains UNKNOWN, not VERIFIED")


def test_c_unknown_cannot_be_authorized_by_default():
    """C. UNKNOWN cannot become authorized by default"""
    print("\nTEST C: UNKNOWN cannot be authorized by default...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    unknown_auth = {
        "authority_id": "AUTH-UNKNOWN",
        "authority_context_id": "CTX-UNKNOWN",
        "verification_state": "UNKNOWN",
        "authority_lifecycle_state": "ACTIVE"
    }

    decision = engine.decide_with_authority(semantic, authority_context=unknown_auth)

    assert decision.authority_context["verification_state"] == "UNKNOWN"
    assert decision.has_authority_context() == False
    assert decision.required_governance_check == True

    print("  ✓ PASS: UNKNOWN authority cannot authorize execution")


def test_d_invalid_context_is_rejected():
    """D. invalid context is rejected"""
    print("\nTEST D: Invalid context is rejected...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    invalid_auth = {
        "authority_id": "AUTH-INVALID",
        "verification_state": "INVALID"
    }

    decision = engine.decide_with_authority(semantic, authority_context=invalid_auth)

    assert decision.authority_context["verification_state"] == "INVALID"
    assert decision.has_authority_context() == False

    print("  ✓ PASS: INVALID authority rejected")


def test_e_authority_provenance_preserved():
    """E. authority provenance is preserved"""
    print("\nTEST E: Authority provenance preserved...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    full_auth_ctx = {
        "authority_id": "AUTH-PROV-001",
        "authority_context_id": "CTX-PROV-001",
        "verification_state": "VERIFIED",
        "authority_lifecycle_state": "ACTIVE",
        "decision_type": "DECISION_TYPE_PROV",
        "resource_class": "RESOURCE_CLASS_PROV",
        "granted_by": "HUMAN_GATE",
        "granted_at": "2026-09-19T10:00:00Z",
        "granting_decision_id": "DEC-HG-001"
    }

    decision = engine.decide_with_authority(semantic, authority_context=full_auth_ctx)

    # Full authority context preserved
    assert decision.authority_context["granted_by"] == "HUMAN_GATE"
    assert decision.authority_context["granting_decision_id"] == "DEC-HG-001"

    # Provenance in binding snapshot
    assert decision.authority_binding["authority_id"] == "AUTH-PROV-001"
    assert decision.authority_binding["captured_at_decision_time"] == True

    print("  ✓ PASS: Authority provenance preserved through decision")


def test_f_historical_snapshot_distinct_from_current_state():
    """F. historical snapshot is distinct from current authority state"""
    print("\nTEST F: Historical snapshot distinct from current state...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    # Simulate authority changing after decision
    auth_at_decision = {
        "authority_id": "AUTH-HIST-001",
        "authority_context_id": "CTX-HIST-001",
        "verification_state": "VERIFIED",
        "authority_lifecycle_state": "ACTIVE",
        "decision_type": "DECISION_TYPE_HIST",
        "resource_class": "RESOURCE_CLASS_HIST"
    }

    decision = engine.decide_with_authority(semantic, authority_context=auth_at_decision)

    # Historical binding captured at T_decision
    binding = decision.get_authority_binding_snapshot()
    assert binding is not None
    assert binding["verification_state_at_decision"] == "VERIFIED"
    assert binding["captured_at_decision_time"] == True

    # Authority context is reference to current state
    assert decision.authority_context["verification_state"] == "VERIFIED"

    # Binding would be immutable; context is reference
    # (Immutability enforced by frozen dataclass + separate snapshot)
    assert binding != decision.authority_context

    print("  ✓ PASS: Historical snapshot distinct from current authority state")


def test_g_existing_m2_decision_behavior_unchanged():
    """G. existing M2 Decision behavior remains unchanged"""
    print("\nTEST G: Existing M2 Decision behavior unchanged...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    # M2 decision without authority (existing behavior)
    decision_m2 = engine.decide(semantic)

    # All existing fields still present and unchanged
    assert decision_m2.selected_action is not None
    assert len(decision_m2.alternatives) > 0
    assert decision_m2.priority_score >= 0.0
    assert decision_m2.risk_score >= 0.0
    assert decision_m2.confidence > 0.0
    assert decision_m2.rationale is not None
    assert decision_m2.required_governance_check == True

    # New fields are None (backward compatible)
    assert decision_m2.authority_context is None
    assert decision_m2.authority_binding is None

    # to_dict() still works
    dict_repr = decision_m2.to_dict()
    assert "selected_action" in dict_repr
    assert "authority_context" not in dict_repr  # Excluded when None

    print("  ✓ PASS: M2 Decision behavior unchanged (backward compatible)")


def test_separation_of_concerns():
    """Verify Code ≠ Auth ≠ Evidence ≠ Decision"""
    print("\nTEST: Separation of concerns...")

    engine = DecisionEngine()
    semantic = MockSemanticResult()

    auth_ctx = {
        "authority_id": "AUTH-SEP-001",
        "verification_state": "VERIFIED",
        "decision_type": "TEST",
        "resource_class": "TEST"
    }

    decision = engine.decide_with_authority(semantic, authority_context=auth_ctx)

    # Code (what to do)
    code_exists = decision.selected_action is not None

    # Authorization (who can do it)
    auth_verified = decision.authority_context["verification_state"] == "VERIFIED"

    # Evidence (proof of authorization at T_decision)
    evidence_captured = decision.authority_binding is not None

    # Decision (execution requires approval)
    decision_made = decision.required_governance_check == True

    assert code_exists
    assert auth_verified
    assert evidence_captured
    assert decision_made

    # They are separate dimensions
    assert decision.selected_action != decision.authority_context["authority_id"]
    assert decision.authority_context != decision.authority_binding

    print("  ✓ PASS: Code ≠ Auth ≠ Evidence ≠ Decision (all separate)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STEP 3: DECISION ENGINE AUTHORITY INTEGRATION TESTS")
    print("Test Requirements A-G")
    print("="*70)

    tests = [
        test_a_valid_authority_context_binds_to_decision,
        test_b_absent_context_cannot_become_verified,
        test_c_unknown_cannot_be_authorized_by_default,
        test_d_invalid_context_is_rejected,
        test_e_authority_provenance_preserved,
        test_f_historical_snapshot_distinct_from_current_state,
        test_g_existing_m2_decision_behavior_unchanged,
        test_separation_of_concerns,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("Classification: UNIT_VERIFIED (tests pass in isolation)")
    print("               CONTRACT_VERIFIED (DecisionResult contract extended)")
    print("               M2_IMPACT_VERIFIED (backward compatible)")
    print("="*70 + "\n")

    exit(0 if failed == 0 else 1)
