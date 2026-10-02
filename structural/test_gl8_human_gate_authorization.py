"""
Unit tests for GL8: Human Gate Authorization Integrity Engine

Test cases for:
  1. Valid decision authorization
  2. Missing decision_id
  3. Decision not found
  4. Inactive decision
  5. Unauthorized approver
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from human_gate_authorization_integrity import (
    HumanGateAuthorizationIntegrityEngine,
    GL8Decision,
    GL8Result
)


class TestGL8HumanGateAuthorization:
    """Test suite for GL8 engine"""

    @pytest.fixture
    def engine(self):
        """Create fresh GL8 engine for each test"""
        return HumanGateAuthorizationIntegrityEngine()

    @pytest.fixture
    def mock_decision_ledger(self, tmp_path):
        """Create mock Decision Ledger file"""
        ledger_dir = tmp_path / "decisions"
        ledger_dir.mkdir()
        ledger_path = ledger_dir / "decision_ledger.jsonl"

        # Write sample decisions
        decisions = [
            {
                "decision_id": "DC_20261002_001",
                "title": "GL8-GL12 Architecture Approval",
                "context": "Test decision",
                "alternatives": [],
                "decision": "APPROVED",
                "rationale": "Test rationale",
                "impact": "Test impact",
                "status": "Active",
                "approved_by": "きむら博士",
                "approved_at": "2026-10-02T01:21:18Z",
                "authorized_scope": ["governance", "structural", "data"]
            },
            {
                "decision_id": "DC_20261001_099",
                "title": "Superseded Decision",
                "status": "Superseded",
                "approved_by": "きむら博士",
                "approved_at": "2026-10-01T00:00:00Z",
                "authorized_scope": []
            },
            {
                "decision_id": "DC_20260930_888",
                "title": "Unauthorized Approver",
                "status": "Active",
                "approved_by": "UnknownEntity",
                "approved_at": "2026-09-30T00:00:00Z",
                "authorized_scope": []
            }
        ]

        with open(ledger_path, "w", encoding="utf-8") as f:
            for decision in decisions:
                f.write(json.dumps(decision) + "\n")

        return ledger_path

    def test_gl8_valid_authorization(self, engine, mock_decision_ledger):
        """Test GL8_OK: Valid authorization passes"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        result = engine.verify_authorization(
            tool_name="mocka_write_event",
            args={"decision_id": "DC_20261002_001"}
        )

        assert result.allowed == True
        assert result.failure_code == "GL8_OK"
        assert result.decision is not None
        assert result.decision.decision_id == "DC_20261002_001"
        assert result.decision.status == "Active"

    def test_gl8_fail_1_missing_decision_id(self, engine):
        """Test GL8_FAIL_1: Missing decision_id"""
        result = engine.verify_authorization(
            tool_name="mocka_write_event",
            args={}  # No decision_id
        )

        assert result.allowed == False
        assert result.failure_code == "GL8_FAIL_1_MISSING_DECISION_ID"
        assert "No decision_id" in result.failure_reason

    def test_gl8_fail_2_decision_not_found(self, engine, mock_decision_ledger):
        """Test GL8_FAIL_2: Decision not found in ledger"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        result = engine.verify_authorization(
            tool_name="mocka_write_event",
            args={"decision_id": "DC_20261002_999"}  # Does not exist
        )

        assert result.allowed == False
        assert result.failure_code == "GL8_FAIL_2_DECISION_NOT_FOUND"
        assert "not found" in result.failure_reason

    def test_gl8_fail_3_inactive_decision(self, engine, mock_decision_ledger):
        """Test GL8_FAIL_3: Decision status not Active"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        result = engine.verify_authorization(
            tool_name="mocka_write_event",
            args={"decision_id": "DC_20261001_099"}  # Superseded
        )

        assert result.allowed == False
        assert result.failure_code == "GL8_FAIL_3_INACTIVE_DECISION"
        assert "not Active" in result.failure_reason

    def test_gl8_fail_4_unauthorized_approver(self, engine, mock_decision_ledger):
        """Test GL8_FAIL_4: Approver not authorized"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        result = engine.verify_authorization(
            tool_name="mocka_write_event",
            args={"decision_id": "DC_20260930_888"}  # UnknownEntity
        )

        assert result.allowed == False
        assert result.failure_code == "GL8_FAIL_4_UNAUTHORIZED_APPROVER"
        assert "not in authorized list" in result.failure_reason

    def test_gl8_get_authorized_scope(self, engine, mock_decision_ledger):
        """Test GL8: Extract authorized_scope for GL9"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        decision = engine._lookup_decision("DC_20261002_001")
        scope = engine.get_authorized_scope(decision)

        assert scope == ["governance", "structural", "data"]

    def test_gl8_caching(self, engine, mock_decision_ledger):
        """Test GL8: Decision caching for performance"""
        engine.DECISION_LEDGER_PATH = mock_decision_ledger

        # First lookup
        decision1 = engine._lookup_decision("DC_20261002_001")

        # Verify it's cached
        assert "DC_20261002_001" in engine.decision_cache

        # Second lookup should use cache
        decision2 = engine._lookup_decision("DC_20261002_001")

        assert decision1.decision_id == decision2.decision_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
