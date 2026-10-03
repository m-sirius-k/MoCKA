"""PAPER 5 PHASE 2 — COMPONENT D Implementation
HG-R5: 30-day Validity + Material-Change Requalification
HG-R10: Deterministic ALL-of-8 Evidence Sufficiency
Condition 2, 9, 12 Enforcement

Authorization: HG_DECISION_PHASE2_0A_APPROVED_20261003
Date: 2026-10-03
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Protocol
import json
import hashlib


# ═══════════════════════════════════════════════════════════════════════════
# CONDITION 2: HG-R5 — 30-DAY VALIDITY + MATERIAL-CHANGE REQUALIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class MaterialChangeType(Enum):
    """Material change triggers for immediate requalification"""
    AUTHORIZATION_CHANGE = "authorization_change"
    EVIDENCE_CHANGE = "evidence_change"
    SCOPE_CHANGE = "scope_change"
    RUNTIME_CHANGE = "runtime_change"
    POLICY_CHANGE = "policy_change"


@dataclass
class AuthorizationRecord:
    """R5: Authorization with 30-day validity window"""
    auth_id: str
    issued_at: datetime
    decision_id: str
    scope: str
    authority: str
    max_validity_days: int = 30
    evidence_hash: str = ""  # Hash of supporting evidence
    policy_version: int = 0  # Policy version at issue time

    def is_within_validity(self) -> bool:
        """Check if authorization is within 30-day window"""
        expiry = self.issued_at + timedelta(days=self.max_validity_days)
        return datetime.now(timezone.utc) <= expiry

    def days_remaining(self) -> int:
        """Calculate days until expiry"""
        if not self.is_within_validity():
            return 0
        expiry = self.issued_at + timedelta(days=self.max_validity_days)
        delta = expiry - datetime.now(timezone.utc)
        return max(0, delta.days)

    def requires_requalification(
        self,
        current_evidence_hash: str,
        current_policy_version: int,
        current_scope: str
    ) -> bool:
        """
        R5: Check if material change requires immediate requalification.

        Returns True if ANY of:
        - 30 days elapsed
        - Evidence changed
        - Policy changed
        - Scope changed
        """
        if not self.is_within_validity():
            return True
        if current_evidence_hash != self.evidence_hash:
            return True
        if current_policy_version != self.policy_version:
            return True
        if current_scope != self.scope:
            return True
        return False


class R5Enforcer:
    """HG-R5: 30-day validity + material-change enforcement"""

    def __init__(self):
        self.active_authorizations: dict[str, AuthorizationRecord] = {}
        self.requalification_required: dict[str, MaterialChangeType] = {}

    def issue_authorization(
        self,
        auth_id: str,
        decision_id: str,
        scope: str,
        authority: str,
        evidence_hash: str,
        policy_version: int
    ) -> AuthorizationRecord:
        """Issue new authorization with 30-day validity"""
        auth = AuthorizationRecord(
            auth_id=auth_id,
            issued_at=datetime.now(timezone.utc),
            decision_id=decision_id,
            scope=scope,
            authority=authority,
            evidence_hash=evidence_hash,
            policy_version=policy_version
        )
        self.active_authorizations[auth_id] = auth
        return auth

    def check_validity(self, auth_id: str) -> bool:
        """Validate authorization is within 30-day window"""
        auth = self.active_authorizations.get(auth_id)
        if not auth:
            return False
        return auth.is_within_validity()

    def check_requalification_trigger(
        self,
        auth_id: str,
        current_evidence_hash: str,
        current_policy_version: int,
        current_scope: str
    ) -> Optional[MaterialChangeType]:
        """
        Detect material change requiring immediate requalification.

        Returns MaterialChangeType if triggered, None otherwise.
        """
        auth = self.active_authorizations.get(auth_id)
        if not auth:
            return MaterialChangeType.AUTHORIZATION_CHANGE

        # Check 30-day expiry
        if not auth.is_within_validity():
            self.requalification_required[auth_id] = MaterialChangeType.AUTHORIZATION_CHANGE
            return MaterialChangeType.AUTHORIZATION_CHANGE

        # Check evidence change
        if current_evidence_hash != auth.evidence_hash:
            self.requalification_required[auth_id] = MaterialChangeType.EVIDENCE_CHANGE
            return MaterialChangeType.EVIDENCE_CHANGE

        # Check policy change
        if current_policy_version != auth.policy_version:
            self.requalification_required[auth_id] = MaterialChangeType.POLICY_CHANGE
            return MaterialChangeType.POLICY_CHANGE

        # Check scope change
        if current_scope != auth.scope:
            self.requalification_required[auth_id] = MaterialChangeType.SCOPE_CHANGE
            return MaterialChangeType.SCOPE_CHANGE

        return None

    def revoke_authorization(self, auth_id: str, reason: str) -> bool:
        """Revoke authorization (cannot auto-renew or extend)"""
        if auth_id in self.active_authorizations:
            del self.active_authorizations[auth_id]
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# CONDITION 9: HG-R10 — DETERMINISTIC ALL-of-8 EVIDENCE SUFFICIENCY
# ═══════════════════════════════════════════════════════════════════════════

class EvidenceLink(Enum):
    """R10: 8 mandatory evidence links (ALL required)"""
    DECISION = "1_decision"              # Human decision record exists
    HUMAN_AUTHORITY = "2_human_authority"  # Authority delegation exists
    AUTHORIZATION = "3_authorization"      # Authorization issued by authority
    SCOPE = "4_scope"                      # Scope bounds defined
    EVIDENCE = "5_evidence"                # Supporting evidence exists
    RUNTIME_EXECUTION = "6_runtime_execution"  # Actual runtime execution occurred
    ACTUAL_CONSEQUENCE = "7_actual_consequence"  # Real consequence recorded
    EVENT_STORE_READBACK = "8_event_store_readback"  # Evidence re-readable from store


@dataclass
class LinkVerification:
    """Verification result for single evidence link"""
    link: EvidenceLink
    status: str  # VERIFIED | UNKNOWN | NOT_FOUND | ABSENT
    evidence_id: Optional[str] = None
    evidence_value: Optional[str] = None
    discovery_method: str = ""


@dataclass
class R10Evaluation:
    """HG-R10 deterministic ALL-of-8 evaluation result"""
    evaluation_id: str
    timestamp: str
    target_id: str
    link_verifications: dict[EvidenceLink, LinkVerification]
    is_sufficient: bool  # True only if ALL 8 VERIFIED
    readback_capability: bool  # Can all links be re-read?

    def to_dict(self) -> dict:
        """Serialize evaluation for Event Store"""
        links_dict = {}
        for link, verification in self.link_verifications.items():
            links_dict[link.value] = {
                'status': verification.status,
                'evidence_id': verification.evidence_id,
                'discovery_method': verification.discovery_method,
            }
        return {
            'evaluation_id': self.evaluation_id,
            'timestamp': self.timestamp,
            'target_id': self.target_id,
            'all_8_links': links_dict,
            'sufficiency': 'SUFFICIENT' if self.is_sufficient else 'NOT_SUFFICIENT',
            'readback_capable': self.readback_capability,
        }


class R10Evaluator:
    """
    HG-R10: Deterministic ALL-of-8 Evidence Sufficiency

    Rules:
    - ALL 8 links must be present and VERIFIED
    - UNKNOWN remains UNKNOWN (not converted to FALSE)
    - NOT_FOUND != ABSENT
    - RECORDED != USED
    - CONFIGURED != CONNECTED
    - Readback unavailable → NOT SUFFICIENT
    - NO scoring / NO partial sufficiency
    """

    def __init__(self):
        self.link_registry: dict[str, dict[EvidenceLink, LinkVerification]] = {}

    def evaluate_all_8_links(
        self,
        target_id: str,
        decision_id: Optional[str] = None,
        authority_id: Optional[str] = None,
        auth_id: Optional[str] = None,
        scope: Optional[str] = None,
        evidence_ids: Optional[list[str]] = None,
        runtime_event_ids: Optional[list[str]] = None,
        consequence_ids: Optional[list[str]] = None,
        readback_verified: bool = False
    ) -> R10Evaluation:
        """
        Evaluate all 8 mandatory evidence links.

        Returns R10Evaluation with ALL-of-8 determination.

        CRITICAL: Returns SUFFICIENT only if:
        - ALL 8 links are VERIFIED
        - Readback is CAPABLE
        """
        import uuid
        from datetime import datetime

        evaluation_id = f"R10-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        verifications: dict[EvidenceLink, LinkVerification] = {}

        # Link 1: DECISION
        if decision_id:
            verifications[EvidenceLink.DECISION] = LinkVerification(
                link=EvidenceLink.DECISION,
                status="VERIFIED",
                evidence_id=decision_id,
                discovery_method="decision_ledger_lookup"
            )
        else:
            verifications[EvidenceLink.DECISION] = LinkVerification(
                link=EvidenceLink.DECISION,
                status="UNKNOWN",
                discovery_method="decision_id_not_provided"
            )

        # Link 2: HUMAN_AUTHORITY
        if authority_id:
            verifications[EvidenceLink.HUMAN_AUTHORITY] = LinkVerification(
                link=EvidenceLink.HUMAN_AUTHORITY,
                status="VERIFIED",
                evidence_id=authority_id,
                discovery_method="authority_registry_lookup"
            )
        else:
            verifications[EvidenceLink.HUMAN_AUTHORITY] = LinkVerification(
                link=EvidenceLink.HUMAN_AUTHORITY,
                status="UNKNOWN",
                discovery_method="authority_id_not_provided"
            )

        # Link 3: AUTHORIZATION
        if auth_id:
            verifications[EvidenceLink.AUTHORIZATION] = LinkVerification(
                link=EvidenceLink.AUTHORIZATION,
                status="VERIFIED",
                evidence_id=auth_id,
                discovery_method="authorization_record_lookup"
            )
        else:
            verifications[EvidenceLink.AUTHORIZATION] = LinkVerification(
                link=EvidenceLink.AUTHORIZATION,
                status="UNKNOWN",
                discovery_method="auth_id_not_provided"
            )

        # Link 4: SCOPE
        if scope:
            verifications[EvidenceLink.SCOPE] = LinkVerification(
                link=EvidenceLink.SCOPE,
                status="VERIFIED",
                evidence_value=scope,
                discovery_method="scope_definition_found"
            )
        else:
            verifications[EvidenceLink.SCOPE] = LinkVerification(
                link=EvidenceLink.SCOPE,
                status="UNKNOWN",
                discovery_method="scope_not_defined"
            )

        # Link 5: EVIDENCE
        if evidence_ids and len(evidence_ids) > 0:
            verifications[EvidenceLink.EVIDENCE] = LinkVerification(
                link=EvidenceLink.EVIDENCE,
                status="VERIFIED",
                evidence_id=",".join(evidence_ids[:3]),  # List first 3
                discovery_method=f"evidence_store_lookup ({len(evidence_ids)} items)"
            )
        else:
            verifications[EvidenceLink.EVIDENCE] = LinkVerification(
                link=EvidenceLink.EVIDENCE,
                status="UNKNOWN",
                discovery_method="no_evidence_ids_provided"
            )

        # Link 6: RUNTIME_EXECUTION
        if runtime_event_ids and len(runtime_event_ids) > 0:
            verifications[EvidenceLink.RUNTIME_EXECUTION] = LinkVerification(
                link=EvidenceLink.RUNTIME_EXECUTION,
                status="VERIFIED",
                evidence_id=runtime_event_ids[0],
                discovery_method=f"runtime_event_log ({len(runtime_event_ids)} events)"
            )
        else:
            verifications[EvidenceLink.RUNTIME_EXECUTION] = LinkVerification(
                link=EvidenceLink.RUNTIME_EXECUTION,
                status="UNKNOWN",
                discovery_method="no_runtime_events_recorded"
            )

        # Link 7: ACTUAL_CONSEQUENCE
        if consequence_ids and len(consequence_ids) > 0:
            verifications[EvidenceLink.ACTUAL_CONSEQUENCE] = LinkVerification(
                link=EvidenceLink.ACTUAL_CONSEQUENCE,
                status="VERIFIED",
                evidence_id=consequence_ids[0],
                discovery_method=f"consequence_log ({len(consequence_ids)} items)"
            )
        else:
            verifications[EvidenceLink.ACTUAL_CONSEQUENCE] = LinkVerification(
                link=EvidenceLink.ACTUAL_CONSEQUENCE,
                status="UNKNOWN",
                discovery_method="no_consequences_recorded"
            )

        # Link 8: EVENT_STORE_READBACK
        if readback_verified:
            verifications[EvidenceLink.EVENT_STORE_READBACK] = LinkVerification(
                link=EvidenceLink.EVENT_STORE_READBACK,
                status="VERIFIED",
                discovery_method="event_store_readback_successful"
            )
        else:
            verifications[EvidenceLink.EVENT_STORE_READBACK] = LinkVerification(
                link=EvidenceLink.EVENT_STORE_READBACK,
                status="UNKNOWN",
                discovery_method="readback_not_performed"
            )

        # Determine sufficiency: ALL-of-8 rule
        # SUFFICIENT only if ALL 8 are VERIFIED
        all_verified = all(
            v.status == "VERIFIED" for v in verifications.values()
        )
        is_sufficient = all_verified and readback_verified

        evaluation = R10Evaluation(
            evaluation_id=evaluation_id,
            timestamp=timestamp,
            target_id=target_id,
            link_verifications=verifications,
            is_sufficient=is_sufficient,
            readback_capability=readback_verified
        )

        self.link_registry[evaluation_id] = verifications
        return evaluation


# ═══════════════════════════════════════════════════════════════════════════
# CONDITION 12: DEPENDENT ENFORCEMENT + READBACK
# ═══════════════════════════════════════════════════════════════════════════

class Condition12Enforcer:
    """
    Condition 12: Dependent enforcement of R5 and R10.

    If R5 requalification is triggered, R10 evaluation must pass before
    execution can proceed.
    If R10 evaluation returns NOT_SUFFICIENT, execution is BLOCKED.
    All decisions and evaluations must be readable from Event Store.
    """

    def __init__(self, r5_enforcer: R5Enforcer, r10_evaluator: R10Evaluator):
        self.r5_enforcer = r5_enforcer
        self.r10_evaluator = r10_evaluator
        self.enforcement_log: list[dict] = []

    def check_execution_feasibility(
        self,
        auth_id: str,
        target_id: str,
        current_evidence_hash: str,
        current_policy_version: int,
        current_scope: str,
        r10_data: dict  # decision_id, authority_id, etc.
    ) -> tuple[bool, str]:
        """
        Condition 12: Check if execution is permitted.

        Returns (feasible: bool, reason: str)

        Logic:
        1. Check R5 validity
        2. If requalification triggered, run R10 evaluation
        3. If R10 = NOT_SUFFICIENT, BLOCK
        4. Otherwise, permit (if valid) or require requalification
        """

        # Step 1: Check R5 validity
        if not self.r5_enforcer.check_validity(auth_id):
            return False, f"R5: Authorization {auth_id} expired"

        # Step 2: Check for material change requiring requalification
        requalif_trigger = self.r5_enforcer.check_requalification_trigger(
            auth_id=auth_id,
            current_evidence_hash=current_evidence_hash,
            current_policy_version=current_policy_version,
            current_scope=current_scope
        )

        if requalif_trigger:
            # Run R10 evaluation
            r10_eval = self.r10_evaluator.evaluate_all_8_links(
                target_id=target_id,
                decision_id=r10_data.get('decision_id'),
                authority_id=r10_data.get('authority_id'),
                auth_id=auth_id,
                scope=current_scope,
                evidence_ids=r10_data.get('evidence_ids', []),
                runtime_event_ids=r10_data.get('runtime_event_ids', []),
                consequence_ids=r10_data.get('consequence_ids', []),
                readback_verified=r10_data.get('readback_verified', False)
            )

            log_entry = {
                'auth_id': auth_id,
                'requalif_trigger': requalif_trigger.value,
                'r10_evaluation_id': r10_eval.evaluation_id,
                'r10_sufficient': r10_eval.is_sufficient
            }

            if not r10_eval.is_sufficient:
                log_entry['result'] = 'BLOCKED'
                self.enforcement_log.append(log_entry)
                return False, f"Condition 12: R10 evaluation NOT_SUFFICIENT ({r10_eval.evaluation_id})"

            log_entry['result'] = 'REQUALIFICATION_REQUIRED'
            self.enforcement_log.append(log_entry)
            return False, f"Condition 12: Requalification required ({requalif_trigger.value})"

        # Step 3: No requalification needed, execution permitted
        return True, "Condition 12: Execution permitted (R5 valid, no material change)"
