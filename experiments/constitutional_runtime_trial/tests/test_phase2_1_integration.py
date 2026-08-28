"""Phase 2-1 Integration Tests: Premise Validation with CR

Tests that the ReEvaluationGate can be integrated and used within the
Constitutional Runtime context without affecting existing CR behavior.

These tests verify:
1. Gate can be instantiated in CR environment
2. Premise validation works correctly (unchanged/changed cases)
3. Execution decision respects premise validation
4. No existing CR behavior is modified
"""

import pytest
from experiments.tim_mocka_comparative.temporal import PastDecision
from experiments.constitutional_runtime_trial.phase2_1_premise_validation import Phase21IntegrationGate


class TestPhase21IntegrationGate:
    """Integration gate operates correctly within CR context."""

    @pytest.fixture
    def gate(self):
        return Phase21IntegrationGate()

    @pytest.fixture
    def now(self):
        return "2026-08-28T12:00:00Z"

    @pytest.fixture
    def unchanged_premises(self, now):
        """Premises that haven't changed."""
        return {
            'past_decision': PastDecision.ALLOW,
            'past_evidence': "evidence-v1",
            'past_validity': "2026-09-30T00:00:00Z",
            'past_authority': "AUTH-01",
            'past_context_id': "CTX-1",
            'past_context_digest': "context-v1",
            'current_evidence': "evidence-v1",
            'current_validity': "2026-09-30T00:00:00Z",
            'current_authority': "AUTH-01",
            'current_context_id': "CTX-1",
            'current_context_digest': "context-v1",
            'now': now,
        }

    def test_gate_instantiation(self, gate):
        """Gate can be created in CR context."""
        assert gate is not None
        assert gate.gate is not None

    def test_unchanged_premises_allows_reuse(self, gate, unchanged_premises):
        """When all premises are unchanged, ALLOW decision can be reused."""
        result = gate.can_reuse_decision(**unchanged_premises)
        assert result['can_reuse'] is True
        assert result['eligibility'] == 'ELIGIBLE'
        assert result['execution'] == 'EXECUTE'
        assert 'PREMISES_UNCHANGED' in result['findings']

    def test_evidence_change_blocks_reuse(self, gate, unchanged_premises):
        """When evidence changes, re-evaluation is required."""
        premises = unchanged_premises.copy()
        premises['current_evidence'] = "evidence-v2"
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'RE_EVALUATE'
        assert result['execution'] == 'STOP'
        assert 'EVIDENCE_CHANGED' in result['findings']

    def test_authority_change_blocks_reuse(self, gate, unchanged_premises):
        """When authority changes, re-evaluation is required."""
        premises = unchanged_premises.copy()
        premises['current_authority'] = "AUTH-02"
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'RE_EVALUATE'
        assert result['execution'] == 'STOP'
        assert 'AUTHORITY_CHANGED' in result['findings']

    def test_context_id_change_blocks_reuse(self, gate, unchanged_premises):
        """When context ID changes, re-evaluation is required."""
        premises = unchanged_premises.copy()
        premises['current_context_id'] = "CTX-2"
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'RE_EVALUATE'
        assert result['execution'] == 'STOP'
        assert 'CONTEXT_MISMATCH' in result['findings']

    def test_context_digest_change_blocks_reuse(self, gate, unchanged_premises):
        """When context digest changes, re-evaluation is required."""
        premises = unchanged_premises.copy()
        premises['current_context_digest'] = "context-v2"
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'RE_EVALUATE'
        assert result['execution'] == 'STOP'
        assert 'CONTEXT_CHANGED' in result['findings']

    def test_block_decision_never_reusable_as_execute(self, gate, unchanged_premises):
        """Past BLOCK is eligible but never executes."""
        premises = unchanged_premises.copy()
        premises['past_decision'] = PastDecision.BLOCK
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'ELIGIBLE'
        assert result['execution'] == 'STOP'

    def test_unknown_decision_stays_unknown(self, gate, unchanged_premises):
        """Past UNKNOWN with unchanged premises stays UNKNOWN."""
        premises = unchanged_premises.copy()
        premises['past_decision'] = PastDecision.UNKNOWN
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'UNKNOWN'
        assert result['execution'] == 'STOP'

    def test_multiple_premise_changes(self, gate, unchanged_premises):
        """Multiple changes detected as multiple findings."""
        premises = unchanged_premises.copy()
        premises['current_evidence'] = "evidence-v2"
        premises['current_authority'] = "AUTH-02"
        result = gate.can_reuse_decision(**premises)
        assert result['can_reuse'] is False
        assert result['eligibility'] == 'RE_EVALUATE'
        assert result['execution'] == 'STOP'
        assert 'EVIDENCE_CHANGED' in result['findings']
        assert 'AUTHORITY_CHANGED' in result['findings']
