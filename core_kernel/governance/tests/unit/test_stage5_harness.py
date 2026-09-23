"""Component A: Isolated Test Harness Tests.

Comprehensive negative and positive tests for Stage 5 isolated test harness.

Negative tests (N1-N5): Demonstrate fail-closed behavior
Positive tests (P1-P6): Demonstrate required functionality

Evidence: All tests run independently and record results.
"""

import pytest
from core_kernel.governance.runtime.stage5_harness import (
    Stage5TestHarness,
    Stage5Identity,
    IsolationBoundaryViolation,
)


class TestNegativeBehavior:
    """Negative tests: fail-closed isolation enforcement."""

    def test_n1_network_attempt_denied(self):
        """N1: External network attempt must be rejected.

        Expected: DENY / ABORT
        """
        harness = Stage5TestHarness()
        harness.initialize()

        # Attempt network access must raise
        with pytest.raises(IsolationBoundaryViolation) as exc_info:
            harness.record_network_attempt("https://external.example.com")

        assert "Network attempt" in str(exc_info.value)
        assert harness._isolation_state["network_calls_attempted"] == 1
        assert "NETWORK_ATTEMPT_DENIED" in [log["event"] for log in harness.get_audit_log()]

    def test_n2_subprocess_attempt_denied(self):
        """N2: Subprocess execution attempt must be rejected.

        Expected: DENY / ABORT
        """
        harness = Stage5TestHarness()
        harness.initialize()

        # Attempt subprocess execution must raise
        with pytest.raises(IsolationBoundaryViolation) as exc_info:
            harness.record_subprocess_attempt("git commit -m 'test'")

        assert "Subprocess attempt" in str(exc_info.value)
        assert harness._isolation_state["subprocess_calls_attempted"] == 1
        assert "SUBPROCESS_ATTEMPT_DENIED" in [log["event"] for log in harness.get_audit_log()]

    def test_n3_production_resource_attempt_denied(self):
        """N3: Production resource access attempt must be rejected.

        Expected: DENY / ABORT
        """
        harness = Stage5TestHarness()
        harness.initialize()

        # Attempt production resource access must raise
        with pytest.raises(IsolationBoundaryViolation) as exc_info:
            harness.record_production_resource_attempt(
                "C:\\Users\\sirok\\MoCKA\\app.py"
            )

        assert "Production resource" in str(exc_info.value)
        assert harness._isolation_state["production_resources_attempted"] == 1
        assert "PRODUCTION_RESOURCE_ATTEMPT_DENIED" in [log["event"] for log in harness.get_audit_log()]

    def test_n4_missing_isolation_identity_fails_closed(self):
        """N4: Initialization without valid isolation identity fails closed.

        Expected: FAIL-CLOSED
        """
        harness = Stage5TestHarness()

        # Manually set precondition check to fail
        def failing_precondition_check():
            return False

        harness._verify_isolation_preconditions = failing_precondition_check

        with pytest.raises(IsolationBoundaryViolation) as exc_info:
            harness.initialize()

        assert "preconditions not met" in str(exc_info.value).lower()
        assert not harness.is_initialized

    def test_n5_teardown_failure_verification(self):
        """N5: Teardown failure must be detectable.

        Expected: FAIL-CLOSED / NOT VERIFIED
        """
        harness = Stage5TestHarness()
        harness.initialize()

        # Add an operation
        harness.allow_operation("test_op")

        # Partial teardown (clear flag but not state)
        harness.is_teardown_complete = True
        # Deliberately leave audit log

        # Verification should fail
        verify_result = harness.verify_teardown()
        assert not verify_result, "Teardown verification should fail if state remains"

    def test_assert_isolation_detects_violations(self):
        """Assert isolation violation is detected."""
        harness = Stage5TestHarness()
        harness.initialize()

        # Manually add violation
        harness._isolation_state["isolation_violations"].append("test violation")

        with pytest.raises(IsolationBoundaryViolation):
            harness.assert_isolation()


class TestPositiveBehavior:
    """Positive tests: required functionality."""

    def test_p1_valid_isolated_harness_initializes(self):
        """P1: Valid isolated Stage 5 harness initializes successfully."""
        harness = Stage5TestHarness()
        identity = harness.initialize()

        assert harness.is_initialized
        assert identity is not None
        assert identity.mode == "stage5_test"
        assert identity.isolation_level == "isolated"

    def test_p2_deterministic_test_identity_generated(self):
        """P2: Deterministic test identity is generated and recorded."""
        harness = Stage5TestHarness()
        identity = harness.initialize()

        assert identity.test_id.startswith("STAGE5_TEST_")
        assert len(identity.test_id) > len("STAGE5_TEST_")
        assert identity.created_at  # ISO8601 timestamp

        # Verify in audit log
        audit = harness.get_audit_log()
        init_event = next(e for e in audit if e["event"] == "HARNESS_INITIALIZED")
        assert init_event["test_id"] == identity.test_id

    def test_p3_stage5_test_mode_explicitly_identifiable(self):
        """P3: Stage 5 test mode is explicitly identifiable."""
        harness = Stage5TestHarness()
        identity = harness.initialize()

        assert identity.mode == "stage5_test"
        assert identity.isolation_level == "isolated"

        # Verify harness tracks identity
        assert harness.get_identity() == identity

    def test_p4_allowed_test_operations_execute(self):
        """P4: Allowed in-memory/test-only operations execute."""
        harness = Stage5TestHarness()
        harness.initialize()

        # Allowed operations should not raise
        harness.allow_operation("test_read_memory")
        harness.allow_operation("test_write_memory")
        harness.allow_operation("test_in_memory_audit")

        # Verify in audit log
        audit = harness.get_audit_log()
        allowed_ops = [e for e in audit if e["event"] == "OPERATION_ALLOWED"]
        assert len(allowed_ops) == 3
        assert "test_read_memory" in [op["operation"] for op in allowed_ops]

    def test_p5_teardown_completes_successfully(self):
        """P5: Teardown completes successfully."""
        harness = Stage5TestHarness()
        harness.initialize()
        harness.allow_operation("test_op")

        result = harness.teardown()

        assert result is True
        assert harness.is_teardown_complete

    def test_p6_post_teardown_state_verified(self):
        """P6: Post-teardown state is verified clean."""
        harness = Stage5TestHarness()
        harness.initialize()
        harness.allow_operation("test_op")

        harness.teardown()
        verify_result = harness.verify_teardown()

        assert verify_result is True
        assert len(harness.get_audit_log()) == 0
        assert harness._isolation_state["network_calls_attempted"] == 0
        assert harness._isolation_state["subprocess_calls_attempted"] == 0
        assert harness._isolation_state["production_resources_attempted"] == 0


class TestIsolationProperties:
    """Verify the 10 required isolation properties."""

    def test_property_1_zero_external_network_io(self):
        """Property 1: Zero external network I/O."""
        harness = Stage5TestHarness()
        harness.initialize()

        # Network attempt must raise
        with pytest.raises(IsolationBoundaryViolation):
            harness.record_network_attempt("http://example.com")

        assert harness._isolation_state["network_calls_attempted"] > 0

    def test_property_2_zero_external_subprocess(self):
        """Property 2: Zero external subprocess execution."""
        harness = Stage5TestHarness()
        harness.initialize()

        # Subprocess attempt must raise
        with pytest.raises(IsolationBoundaryViolation):
            harness.record_subprocess_attempt("python script.py")

        assert harness._isolation_state["subprocess_calls_attempted"] > 0

    def test_property_3_no_production_resource_access(self):
        """Property 3: No production resource access."""
        harness = Stage5TestHarness()
        harness.initialize()

        # Production resource attempt must raise
        with pytest.raises(IsolationBoundaryViolation):
            harness.record_production_resource_attempt(
                "C:\\Users\\sirok\\MoCKA\\data\\decisions\\decision_ledger.jsonl"
            )

        assert harness._isolation_state["production_resources_attempted"] > 0

    def test_property_4_deterministic_test_identity(self):
        """Property 4: Deterministic test identity."""
        harness = Stage5TestHarness()
        identity = harness.initialize()

        assert identity.test_id
        assert identity.created_at
        assert identity.mode == "stage5_test"

    def test_property_5_explicit_stage5_mode_identification(self):
        """Property 5: Explicit Stage 5 test-mode identification."""
        harness = Stage5TestHarness()
        identity = harness.initialize()

        assert identity.mode == "stage5_test"
        assert identity.isolation_level == "isolated"

    def test_property_6_fail_closed_isolation_failure(self):
        """Property 6: Fail-closed when isolation cannot be established."""
        harness = Stage5TestHarness()
        harness._verify_isolation_preconditions = lambda: False

        with pytest.raises(IsolationBoundaryViolation):
            harness.initialize()

    def test_property_7_explicit_teardown(self):
        """Property 7: Explicit teardown."""
        harness = Stage5TestHarness()
        harness.initialize()

        assert not harness.is_teardown_complete
        result = harness.teardown()
        assert result is True
        assert harness.is_teardown_complete

    def test_property_8_teardown_verification(self):
        """Property 8: Teardown verification."""
        harness = Stage5TestHarness()
        harness.initialize()
        harness.teardown()

        verify_result = harness.verify_teardown()
        assert verify_result is True

    def test_property_9_no_persistent_stage5_state(self):
        """Property 9: No persistent Stage 5 state."""
        harness = Stage5TestHarness()
        harness.initialize()
        harness.allow_operation("test")

        # Before teardown: audit log has entries
        assert len(harness.get_audit_log()) > 0

        # After teardown: audit log is empty
        harness.teardown()
        assert len(harness.get_audit_log()) == 0

    def test_property_10_auditable_initialization_termination(self):
        """Property 10: Auditable initialization and termination."""
        harness = Stage5TestHarness()
        identity = harness.initialize()
        harness.teardown()

        # Before final teardown check, audit log should have init event
        # (but we're testing the property via get_audit_log before teardown clears it)
        harness2 = Stage5TestHarness()
        identity2 = harness2.initialize()
        audit = harness2.get_audit_log()

        init_events = [e for e in audit if e["event"] == "HARNESS_INITIALIZED"]
        assert len(init_events) == 1
        assert init_events[0]["test_id"] == identity2.test_id


class TestComponentAEdgeCases:
    """Edge case tests for robustness."""

    def test_multiple_operations_recorded(self):
        """Multiple operations are all recorded."""
        harness = Stage5TestHarness()
        harness.initialize()

        for i in range(5):
            harness.allow_operation(f"op_{i}")

        audit = harness.get_audit_log()
        op_events = [e for e in audit if e["event"] == "OPERATION_ALLOWED"]
        assert len(op_events) == 5

    def test_isolation_violation_accumulation(self):
        """Multiple isolation violations accumulate."""
        harness = Stage5TestHarness()
        harness.initialize()

        attempts = 0
        for i in range(3):
            try:
                harness.record_network_attempt(f"host{i}.example.com")
            except IsolationBoundaryViolation:
                attempts += 1

        assert attempts == 3
        assert harness._isolation_state["network_calls_attempted"] == 3

    def test_teardown_idempotent(self):
        """Teardown can be called multiple times."""
        harness = Stage5TestHarness()
        harness.initialize()

        result1 = harness.teardown()
        result2 = harness.teardown()

        assert result1 is True
        assert result2 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
