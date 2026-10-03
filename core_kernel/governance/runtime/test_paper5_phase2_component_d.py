"""
PAPER 5 PHASE 2 — COMPONENT D TEST SUITE
R5 (Condition 2) + R10 (Condition 9) + Condition 12 Verification

Mandatory tests:
- R5 enforcement (30-day + material-change)
- R10 enforcement (ALL-of-8 deterministic)
- Condition 12 dependent enforcement
"""

import unittest
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from paper5_phase2_component_d import (
    R5Enforcer, MaterialChangeType, AuthorizationRecord,
    R10Evaluator, EvidenceLink, LinkVerification,
    Condition12Enforcer
)


# ═══════════════════════════════════════════════════════════════════════════
# R5 TESTS — CONDITION 2 (30-day Validity + Material-Change Triggers)
# ═══════════════════════════════════════════════════════════════════════════

class TestR5Enforcement(unittest.TestCase):
    """HG-R5: 30-day validity + material-change requalification"""

    def setUp(self):
        self.enforcer = R5Enforcer()

    def test_r5_01_authorization_issued_within_30_days(self):
        """R5.1: Authorization valid within 30 days"""
        auth = self.enforcer.issue_authorization(
            auth_id="AUTH-001",
            decision_id="DC-001",
            scope="component_d",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        self.assertTrue(self.enforcer.check_validity("AUTH-001"))
        self.assertGreater(auth.days_remaining(), 0)

    def test_r5_02_authorization_expired_after_30_days(self):
        """R5.2: Authorization invalid after 30 days"""
        auth = AuthorizationRecord(
            auth_id="AUTH-002",
            issued_at=datetime.now(timezone.utc) - timedelta(days=31),
            decision_id="DC-002",
            scope="component_d",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        self.enforcer.active_authorizations["AUTH-002"] = auth
        self.assertFalse(self.enforcer.check_validity("AUTH-002"))
        self.assertEqual(auth.days_remaining(), 0)

    def test_r5_03_material_change_evidence_triggers_requalification(self):
        """R5.3: Evidence change triggers immediate requalification"""
        self.enforcer.issue_authorization(
            auth_id="AUTH-003",
            decision_id="DC-003",
            scope="component_d",
            authority="human_gate",
            evidence_hash="old_hash",
            policy_version=1
        )
        # Evidence changed
        trigger = self.enforcer.check_requalification_trigger(
            auth_id="AUTH-003",
            current_evidence_hash="new_hash",
            current_policy_version=1,
            current_scope="component_d"
        )
        self.assertEqual(trigger, MaterialChangeType.EVIDENCE_CHANGE)

    def test_r5_04_material_change_policy_triggers_requalification(self):
        """R5.4: Policy version change triggers immediate requalification"""
        self.enforcer.issue_authorization(
            auth_id="AUTH-004",
            decision_id="DC-004",
            scope="component_d",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        # Policy changed
        trigger = self.enforcer.check_requalification_trigger(
            auth_id="AUTH-004",
            current_evidence_hash="abc123",
            current_policy_version=2,  # Changed
            current_scope="component_d"
        )
        self.assertEqual(trigger, MaterialChangeType.POLICY_CHANGE)

    def test_r5_05_material_change_scope_triggers_requalification(self):
        """R5.5: Scope change triggers immediate requalification"""
        self.enforcer.issue_authorization(
            auth_id="AUTH-005",
            decision_id="DC-005",
            scope="component_d_original",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        # Scope changed
        trigger = self.enforcer.check_requalification_trigger(
            auth_id="AUTH-005",
            current_evidence_hash="abc123",
            current_policy_version=1,
            current_scope="component_d_modified"  # Changed
        )
        self.assertEqual(trigger, MaterialChangeType.SCOPE_CHANGE)

    def test_r5_06_no_requalification_when_all_stable(self):
        """R5.6: No requalification when authority/evidence/policy/scope unchanged"""
        self.enforcer.issue_authorization(
            auth_id="AUTH-006",
            decision_id="DC-006",
            scope="component_d",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        trigger = self.enforcer.check_requalification_trigger(
            auth_id="AUTH-006",
            current_evidence_hash="abc123",
            current_policy_version=1,
            current_scope="component_d"
        )
        self.assertIsNone(trigger)

    def test_r5_07_revoke_authorization(self):
        """R5.7: Authorization can be revoked (no auto-renewal)"""
        self.enforcer.issue_authorization(
            auth_id="AUTH-007",
            decision_id="DC-007",
            scope="component_d",
            authority="human_gate",
            evidence_hash="abc123",
            policy_version=1
        )
        self.assertTrue(self.enforcer.check_validity("AUTH-007"))
        self.enforcer.revoke_authorization("AUTH-007", "test_revocation")
        self.assertFalse(self.enforcer.check_validity("AUTH-007"))


# ═══════════════════════════════════════════════════════════════════════════
# R10 TESTS — CONDITION 9 (Deterministic ALL-of-8 Evidence Sufficiency)
# ═══════════════════════════════════════════════════════════════════════════

class TestR10Enforcement(unittest.TestCase):
    """HG-R10: ALL-of-8 deterministic evidence sufficiency"""

    def setUp(self):
        self.evaluator = R10Evaluator()

    def test_r10_01_missing_decision_link_not_sufficient(self):
        """R10.1: Missing decision link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T001",
            decision_id=None,  # MISSING
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.DECISION].status, "UNKNOWN")

    def test_r10_02_missing_authority_link_not_sufficient(self):
        """R10.2: Missing human authority link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T002",
            decision_id="DC001",
            authority_id=None,  # MISSING
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.HUMAN_AUTHORITY].status, "UNKNOWN")

    def test_r10_03_missing_authorization_link_not_sufficient(self):
        """R10.3: Missing authorization link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T003",
            decision_id="DC001",
            authority_id="AU001",
            auth_id=None,  # MISSING
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.AUTHORIZATION].status, "UNKNOWN")

    def test_r10_04_missing_scope_link_not_sufficient(self):
        """R10.4: Missing scope link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T004",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope=None,  # MISSING
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.SCOPE].status, "UNKNOWN")

    def test_r10_05_missing_evidence_link_not_sufficient(self):
        """R10.5: Missing evidence link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T005",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=[],  # MISSING
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.EVIDENCE].status, "UNKNOWN")

    def test_r10_06_missing_runtime_execution_link_not_sufficient(self):
        """R10.6: Missing runtime execution link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T006",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=[],  # MISSING
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.RUNTIME_EXECUTION].status, "UNKNOWN")

    def test_r10_07_missing_consequence_link_not_sufficient(self):
        """R10.7: Missing actual consequence link → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T007",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=[],  # MISSING
            readback_verified=True
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.ACTUAL_CONSEQUENCE].status, "UNKNOWN")

    def test_r10_08_missing_readback_not_sufficient(self):
        """R10.8: Readback unavailable → NOT_SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T008",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=False  # MISSING READBACK
        )
        self.assertFalse(eval.is_sufficient)
        self.assertEqual(eval.link_verifications[EvidenceLink.EVENT_STORE_READBACK].status, "UNKNOWN")

    def test_r10_09_all_8_links_sufficient(self):
        """R10.9: All 8 links present → SUFFICIENT"""
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T009",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1", "E2"],
            runtime_event_ids=["RT1"],
            consequence_ids=["C1"],
            readback_verified=True
        )
        self.assertTrue(eval.is_sufficient)
        # All links should be VERIFIED
        for link in EvidenceLink:
            self.assertEqual(eval.link_verifications[link].status, "VERIFIED")

    def test_r10_10_partial_evidence_not_converted_to_sufficient(self):
        """R10.10: Partial evidence (7/8) stays NOT_SUFFICIENT (no scoring)"""
        # Missing only 1 link (consequence)
        eval = self.evaluator.evaluate_all_8_links(
            target_id="T010",
            decision_id="DC001",
            authority_id="AU001",
            auth_id="AUTH001",
            scope="test",
            evidence_ids=["E1"],
            runtime_event_ids=["RT1"],
            consequence_ids=[],  # MISSING 1 link
            readback_verified=True
        )
        # Still NOT sufficient (NO scoring/partial)
        self.assertFalse(eval.is_sufficient)


# ═══════════════════════════════════════════════════════════════════════════
# CONDITION 12 TESTS — Dependent Enforcement
# ═══════════════════════════════════════════════════════════════════════════

class TestCondition12Enforcement(unittest.TestCase):
    """Condition 12: Dependent enforcement of R5 + R10"""

    def setUp(self):
        self.r5 = R5Enforcer()
        self.r10 = R10Evaluator()
        self.enforcer = Condition12Enforcer(self.r5, self.r10)

    def test_cond12_01_valid_auth_no_material_change_permits_execution(self):
        """Condition 12.1: Valid auth + no material change → execution permitted"""
        self.r5.issue_authorization(
            auth_id="AUTH-C12-01",
            decision_id="DC-001",
            scope="test",
            authority="hg",
            evidence_hash="hash1",
            policy_version=1
        )
        feasible, reason = self.enforcer.check_execution_feasibility(
            auth_id="AUTH-C12-01",
            target_id="T001",
            current_evidence_hash="hash1",
            current_policy_version=1,
            current_scope="test",
            r10_data={'decision_id': 'DC-001'}
        )
        self.assertTrue(feasible)
        self.assertIn("permitted", reason)

    def test_cond12_02_expired_auth_blocks_execution(self):
        """Condition 12.2: Expired authorization → execution blocked"""
        # Create expired auth
        auth = AuthorizationRecord(
            auth_id="AUTH-C12-02",
            issued_at=datetime.now(timezone.utc) - timedelta(days=31),
            decision_id="DC-002",
            scope="test",
            authority="hg",
            evidence_hash="hash1",
            policy_version=1
        )
        self.r5.active_authorizations["AUTH-C12-02"] = auth

        feasible, reason = self.enforcer.check_execution_feasibility(
            auth_id="AUTH-C12-02",
            target_id="T002",
            current_evidence_hash="hash1",
            current_policy_version=1,
            current_scope="test",
            r10_data={}
        )
        self.assertFalse(feasible)
        self.assertIn("expired", reason.lower())

    def test_cond12_03_material_change_with_r10_sufficient_allows_requalification_flow(self):
        """Condition 12.3: Material change → R10 run → if sufficient, requalification flow"""
        self.r5.issue_authorization(
            auth_id="AUTH-C12-03",
            decision_id="DC-003",
            scope="test",
            authority="hg",
            evidence_hash="hash1",
            policy_version=1
        )
        # Evidence changed
        feasible, reason = self.enforcer.check_execution_feasibility(
            auth_id="AUTH-C12-03",
            target_id="T003",
            current_evidence_hash="hash2",  # Changed
            current_policy_version=1,
            current_scope="test",
            r10_data={
                'decision_id': 'DC-003',
                'authority_id': 'AU-001',
                'evidence_ids': ['E1'],
                'runtime_event_ids': ['RT1'],
                'consequence_ids': ['C1'],
                'readback_verified': True
            }
        )
        self.assertFalse(feasible)
        self.assertIn("Requalification required", reason)

    def test_cond12_04_material_change_with_r10_not_sufficient_blocks(self):
        """Condition 12.4: Material change → R10 NOT_SUFFICIENT → BLOCK"""
        self.r5.issue_authorization(
            auth_id="AUTH-C12-04",
            decision_id="DC-004",
            scope="test",
            authority="hg",
            evidence_hash="hash1",
            policy_version=1
        )
        # Evidence changed + R10 will fail (missing evidence)
        feasible, reason = self.enforcer.check_execution_feasibility(
            auth_id="AUTH-C12-04",
            target_id="T004",
            current_evidence_hash="hash2",  # Changed
            current_policy_version=1,
            current_scope="test",
            r10_data={
                'decision_id': 'DC-004',
                'authority_id': 'AU-001',
                'evidence_ids': [],  # MISSING - R10 will fail
                'runtime_event_ids': [],
                'consequence_ids': [],
                'readback_verified': False
            }
        )
        self.assertFalse(feasible)
        self.assertIn("NOT_SUFFICIENT", reason)


if __name__ == '__main__':
    unittest.main()
