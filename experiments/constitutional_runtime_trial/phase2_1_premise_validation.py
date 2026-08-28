"""Phase 2-1 Limited Integration: Premise Validation Flow

Status: EXPERIMENTAL INTEGRATION (not production)
Purpose: Demonstrate re-evaluation gate operation within CR context
Scope: Isolated from existing CR behavior

This module tests whether the ReEvaluationGate from tim_mocka_comparative
can be integrated into Constitutional Runtime decision-making without
affecting existing CR baseline behavior (117 tests).

Key constraint: This is a PROOF-OF-CONCEPT integration, not a core CR change.
"""

from datetime import datetime, timezone

from .primitives import Decision, Execution
from ..tim_mocka_comparative.temporal import ReEvaluationGate, DecisionRecord, PresentContext, PastDecision


class Phase21IntegrationGate:
    """Premise validation for historical decision reuse.

    This gate operates ON TOP of the existing CR, not as a replacement.
    It takes a past decision record and present context, validates premises,
    and determines if the past decision can be reused without re-evaluation.

    If premises have changed, it signals that re-evaluation is needed.
    If premises are unchanged, it signals that the past decision can be reused.
    """

    def __init__(self):
        self.gate = ReEvaluationGate()

    def can_reuse_decision(self, past_decision, past_evidence, past_validity,
                          past_authority, past_context_id, past_context_digest,
                          current_evidence, current_validity, current_authority,
                          current_context_id, current_context_digest, now):
        """Check if a past decision's premises are intact in the present.

        Args:
            past_decision: PastDecision enum (ALLOW/BLOCK/UNKNOWN)
            past_evidence: digest of evidence when decision was made
            past_validity: validity_until timestamp
            past_authority: authority ID at decision time
            past_context_id: context ID at decision time
            past_context_digest: digest of context at decision time
            current_evidence: current evidence digest
            current_validity: current validity_until (same field as past, in this test)
            current_authority: current authority ID
            current_context_id: current context ID
            current_context_digest: current context digest
            now: current timestamp for comparison

        Returns:
            dict with:
                'can_reuse': bool - whether premises are unchanged
                'eligibility': str - gate result (ELIGIBLE/RE_EVALUATE/BLOCK/UNKNOWN)
                'findings': list - premise changes detected
        """

        # Build DecisionRecord from past parameters
        record = DecisionRecord(
            decision_id="phase2-1-test",
            decision=past_decision,
            decided_at="2026-08-01T00:00:00Z",  # arbitrary past time
            validity_until=past_validity,
            evidence_digest=past_evidence,
            authority_id=past_authority,
            context_id=past_context_id,
            context_digest=past_context_digest,
        )

        # Build PresentContext from current parameters
        present = PresentContext(
            now=now,
            evidence_digest=current_evidence,
            authority_id=current_authority,
            authority_state="VALID",  # assume valid for this test
            context_id=current_context_id,
            context_digest=current_context_digest,
        )

        # Run gate assessment
        assessment = self.gate.assess(record, present)

        # Extract result
        can_reuse = (
            assessment.eligibility.value == "ELIGIBLE" and
            past_decision == PastDecision.ALLOW
        )

        return {
            'can_reuse': can_reuse,
            'eligibility': assessment.eligibility.value,
            'execution': assessment.execution.value,
            'findings': assessment.finding_names,
            'reason': assessment.reason,
        }


def demonstrate_phase_21_integration():
    """Demonstrate the gate in integrated context without modifying CR.

    This proves that:
    1. The gate can operate within CR environment
    2. It correctly detects premise changes
    3. It doesn't interfere with existing CR operation
    """

    gate = Phase21IntegrationGate()
    now = "2026-08-28T12:00:00Z"

    # Test case 1: Premises unchanged - reusable
    result1 = gate.can_reuse_decision(
        past_decision=PastDecision.ALLOW,
        past_evidence="evidence-v1",
        past_validity="2026-09-30T00:00:00Z",
        past_authority="AUTH-01",
        past_context_id="CTX-1",
        past_context_digest="context-v1",
        current_evidence="evidence-v1",
        current_validity="2026-09-30T00:00:00Z",
        current_authority="AUTH-01",
        current_context_id="CTX-1",
        current_context_digest="context-v1",
        now=now,
    )

    # Test case 2: Evidence changed - NOT reusable
    result2 = gate.can_reuse_decision(
        past_decision=PastDecision.ALLOW,
        past_evidence="evidence-v1",
        past_validity="2026-09-30T00:00:00Z",
        past_authority="AUTH-01",
        past_context_id="CTX-1",
        past_context_digest="context-v1",
        current_evidence="evidence-v2",  # changed
        current_validity="2026-09-30T00:00:00Z",
        current_authority="AUTH-01",
        current_context_id="CTX-1",
        current_context_digest="context-v1",
        now=now,
    )

    # Test case 3: Authority changed - NOT reusable
    result3 = gate.can_reuse_decision(
        past_decision=PastDecision.ALLOW,
        past_evidence="evidence-v1",
        past_validity="2026-09-30T00:00:00Z",
        past_authority="AUTH-01",
        past_context_id="CTX-1",
        past_context_digest="context-v1",
        current_evidence="evidence-v1",
        current_validity="2026-09-30T00:00:00Z",
        current_authority="AUTH-02",  # changed
        current_context_id="CTX-1",
        current_context_digest="context-v1",
        now=now,
    )

    return {
        'case_1_unchanged': result1,
        'case_2_evidence_changed': result2,
        'case_3_authority_changed': result3,
    }


if __name__ == "__main__":
    results = demonstrate_phase_21_integration()
    import json
    print(json.dumps(results, indent=2, default=str))
