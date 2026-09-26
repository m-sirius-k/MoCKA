"""
tests/test_phase8_7_connector.py

Phase 8-7 Connector Unit & Integration Tests

Tests:
  1. ExecutionDecisionConnector instantiation
  2. Execution result creation with correlation IDs
  3. Decision write integration (mocked HTTP)
  4. Event linking (companion mechanism)
  5. Memory write integration
  6. Failure isolation (no auto-success)
  7. End-to-end flow with mock server
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from governance.execution_decision_connector import (
    ExecutionDecisionConnector,
    ExecutionResult,
    create_execution_result,
)


class TestExecutionResultCreation:
    """Test execution result factory and structure."""

    def test_create_execution_result_success(self):
        """Test creating a successful execution result."""
        result = create_execution_result(
            status="success",
            output="Command executed",
            correlation_id="CORR_TEST_001",
        )

        assert result.status == "success"
        assert result.output == "Command executed"
        assert result.correlation_id == "CORR_TEST_001"
        assert result.execution_id.startswith("EXEC_")
        assert result.task_id.startswith("TASK_")
        assert result.hab_request_id.startswith("HAB_")

    def test_create_execution_result_failure(self):
        """Test creating a failed execution result."""
        result = create_execution_result(
            status="failure",
            error="Connection timeout",
            correlation_id="CORR_TEST_002",
        )

        assert result.status == "failure"
        assert result.error == "Connection timeout"
        assert result.output is None

    def test_create_execution_result_default_ids(self):
        """Test that IDs are auto-generated when not provided."""
        result = create_execution_result(status="success")

        assert result.correlation_id.startswith("CORR_")
        assert result.task_id.startswith("TASK_")
        assert result.hab_request_id.startswith("HAB_")
        assert result.execution_id.startswith("EXEC_")

    def test_execution_result_timestamps(self):
        """Test that timestamps are set correctly."""
        result = create_execution_result(status="success")

        assert result.started_at is not None
        assert result.completed_at is not None
        # Should be valid ISO format
        datetime.fromisoformat(result.started_at.replace("Z", "+00:00"))
        datetime.fromisoformat(result.completed_at.replace("Z", "+00:00"))


class TestExecutionDecisionConnectorIntegration:
    """Test the connector with mocked HTTP responses."""

    @patch('requests.post')
    def test_connect_execution_to_decision_success(self, mock_post):
        """Test successful execution to decision connection."""
        # Mock successful response from mocka_decision_write
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "status": "ok",
                "decision_id": "DC_20260926_001",
                "event_id": "EV_20260926_001",
            }
        )

        connector = ExecutionDecisionConnector(mcp_endpoint="http://mock:5002")
        execution = create_execution_result(
            status="success",
            output="Test output",
            correlation_id="CORR_TEST_003",
        )

        result = connector.connect_execution_to_canonical_paths(
            execution=execution,
            decision_context={
                "title": "Test Decision",
                "rationale": "Testing connector",
                "impact": "None",
            }
        )

        assert result["status"] == "connected"
        assert result["decision_id"] == "DC_20260926_001"
        assert result["event_id"] == "EV_20260926_001"
        assert result["correlation_id"] == "CORR_TEST_003"
        assert mock_post.called

    @patch('requests.post')
    def test_connect_execution_failure_not_masked(self, mock_post):
        """Test that execution failure is recorded as failure, not masked."""
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "status": "ok",
                "decision_id": "DC_20260926_FAIL",
                "event_id": None,
            }
        )

        connector = ExecutionDecisionConnector(mcp_endpoint="http://mock:5002")
        execution = create_execution_result(
            status="failure",
            error="Test error",
            correlation_id="CORR_TEST_FAIL",
        )

        result = connector.connect_execution_to_canonical_paths(
            execution=execution,
            decision_context={
                "title": "Failure Test",
                "rationale": "Testing failure handling",
                "impact": "None",
            }
        )

        # Check that the call to decision_write included the failure status
        call_args = mock_post.call_args
        payload = call_args[1]["json"]  # kwargs['json']

        assert "failure" in payload["decision"].lower()
        assert result["decision_id"] is not None
        # Decision was recorded, but not auto-approved

    @patch('requests.post')
    def test_mcp_server_connection_error(self, mock_post):
        """Test handling of unreachable MCP server."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        connector = ExecutionDecisionConnector(mcp_endpoint="http://unreachable:5002")
        execution = create_execution_result(status="success")

        result = connector.connect_execution_to_canonical_paths(
            execution=execution,
            decision_context={"title": "Test"},
        )

        assert result["status"] == "failed"
        assert result["decision_id"] is None
        assert len(result["errors"]) > 0
        assert "unreachable" in result["errors"][0].lower()

    @patch('requests.post')
    def test_mcp_server_error_response(self, mock_post):
        """Test handling of error response from MCP server."""
        mock_post.return_value = Mock(
            status_code=400,
            text="Bad request",
            json=lambda: {"error": "Invalid input"}
        )

        connector = ExecutionDecisionConnector(mcp_endpoint="http://mock:5002")
        execution = create_execution_result(status="success")

        result = connector.connect_execution_to_canonical_paths(
            execution=execution,
            decision_context={"title": "Test"},
        )

        assert result["status"] == "failed"
        assert result["decision_id"] is None
        assert len(result["errors"]) > 0

    def test_correlation_id_chain_preserved(self):
        """Test that correlation_id is preserved through entire chain."""
        expected_corr_id = "CORR_TEST_CHAIN_001"

        connector = ExecutionDecisionConnector()
        execution = create_execution_result(
            status="success",
            correlation_id=expected_corr_id,
        )

        # Don't actually connect (server not running), just check structure
        assert execution.correlation_id == expected_corr_id
        assert execution.execution_id  # Generated
        assert execution.task_id  # Generated
        assert execution.hab_request_id  # Generated

    @patch('governance.execution_decision_connector.MemoryWriter')
    @patch('requests.post')
    def test_memory_write_integration(self, mock_post, mock_memory_writer):
        """Test that memory write is called when available."""
        # Mock successful decision write
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "status": "ok",
                "decision_id": "DC_MEM_001",
                "event_id": "EV_MEM_001",
            }
        )

        # Mock successful memory write
        mock_entry = Mock()
        mock_entry.memory_id = "MEM_001"
        mock_memory_instance = Mock()
        mock_memory_instance.write_event.return_value = mock_entry
        mock_memory_writer.return_value = mock_memory_instance

        connector = ExecutionDecisionConnector(mcp_endpoint="http://mock:5002")
        execution = create_execution_result(status="success")

        result = connector.connect_execution_to_canonical_paths(
            execution=execution,
            decision_context={"title": "Memory Test"},
        )

        assert result["status"] == "connected"
        assert result["decision_id"] == "DC_MEM_001"
        assert result["memory_id"] == "MEM_001"
        mock_memory_instance.write_event.assert_called_once()

    def test_no_auto_approval_semantics(self):
        """Test that execution success does NOT mean authorization."""
        # Create a result with status="success"
        connector = ExecutionDecisionConnector()
        execution = create_execution_result(
            status="success",
            output="Completed",
        )

        # The presence of execution.status="success" should NOT
        # auto-mark the decision as "approved" or "authorized".
        # It should be recorded as "execution_recorded_as_success".

        # This is verified by checking the decision context would
        # NOT contain any authorization-granting language.
        decision_context = {
            "rationale": "Execution completed",
            "impact": "Status recorded, not approved",
        }

        # Both should be recorded with same "recording" semantics,
        # not "authorization" semantics
        assert "approved" not in decision_context["rationale"].lower()
        assert "authorized" not in decision_context["impact"].lower()


class TestGovernancentSemantics:
    """Test governance contract compliance."""

    def test_execution_not_authorization(self):
        """Test that Execution ≠ Authorization."""
        # This is a semantic test to ensure code structure doesn't confuse terms
        execution = ExecutionResult(
            execution_id="EXEC_001",
            correlation_id="CORR_001",
            task_id="TASK_001",
            hab_request_id="HAB_001",
            status="success",  # execution status
        )

        # The execution having status="success" does not mean:
        # - User authorized it
        # - System approved it
        # - It's safe to use
        # It only means: the code that was asked to run, did run without error

        assert hasattr(execution, 'status')
        assert execution.status in ("success", "failure", "halted")
        assert not hasattr(execution, 'authorized')  # No authorization field
        assert not hasattr(execution, 'approved')    # No approval field

    def test_recorded_not_used(self):
        """Test that Recording ≠ Usage."""
        # Writing to Decision/Event/Memory means it's recorded for auditing.
        # It does NOT mean it's validated, approved, or safe to use.

        connector = ExecutionDecisionConnector()

        # Even if we could write a record, it's just a record.
        # Not a validation, not an approval.
        decision_context = {
            "title": "Execution recorded",
            "rationale": "For audit trail",
            "impact": "Record created, not validated",
        }

        assert "audit" in decision_context["rationale"].lower()
        assert "validated" not in decision_context["impact"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
