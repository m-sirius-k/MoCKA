"""
aur/enforcement.py: A AND U AND R single enforcement point.

This is the ONLY place where all three conditions are evaluated together.
No bypass. No partial evaluation.

Contract: docs/contracts/action_execution_contract_v1.md (Stage 5)

BA04 bypass prevention:
  - gate=None -> DENY (not ALLOW)
  - gate.status != "APPROVED" -> DENY
  - assessment=None -> DENY
  - gl7=None -> DENY
  - fail-closed on any exception
"""
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from aur.assessment import AssessmentRecord, CONFIDENCE_THRESHOLD, is_assessment_fresh


APPROVED_GATE_STATUSES = {"APPROVED"}


@dataclass
class EnforcementRecord:
    enforcement_id: str
    action_id: str
    timestamp: str
    decision: str
    reason: str
    assessment_id: Optional[str]
    gate_status: Optional[str]
    gl7_approved: Optional[bool]
    gl7_aborts: list


def _generate_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"ENFOR-{today}-{uuid.uuid4().hex[:8]}"


class EnforcementPoint:
    """
    Single A AND U AND R enforcement point.

    check(assessment, gate_result, gl7_result) -> dict with:
      - decision: "ALLOW" | "DENY"
      - reason: str
      - enforcement_id: str
      - details: dict
    """

    def check(
        self,
        assessment: Optional[AssessmentRecord],
        gate_result: Optional[dict],
        gl7_result: Optional[dict],
    ) -> dict:
        """
        Evaluate A AND U AND R simultaneously.

        assessment:  AssessmentRecord (or dict with same fields, or None)
        gate_result: dict from Human Gate with at least {"status": ...}
        gl7_result:  dict from GL7 with at least {"approved": bool, "aborts": [...]}

        Returns dict:
          decision: "ALLOW" | "DENY"
          reason: str
          enforcement_id: str
          details: {a_ok, u_ok, r_ok, ...}
        """
        enforcement_id = _generate_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            a_ok, a_reason, assessment_id, confidence = self._check_assessment(assessment)
            u_ok, u_reason, gate_status = self._check_authorization(gate_result)
            r_ok, r_reason, gl7_approved, gl7_aborts = self._check_runtime(gl7_result)

            if a_ok and u_ok and r_ok:
                decision = "ALLOW"
                reason = "A AND U AND R all satisfied"
            else:
                decision = "DENY"
                parts = []
                if not a_ok:
                    parts.append(f"assessment: {a_reason}")
                if not u_ok:
                    parts.append(f"human_gate: {u_reason}")
                if not r_ok:
                    parts.append(f"runtime: {r_reason}")
                reason = "; ".join(parts)

        except Exception as exc:
            decision = "DENY"
            reason = f"enforcement exception (fail-closed): {exc}"
            enforcement_id = enforcement_id
            assessment_id = None
            confidence = None
            gate_status = None
            gl7_approved = None
            gl7_aborts = []
            a_ok = u_ok = r_ok = False

        action_id = "unknown"
        if assessment is not None:
            if isinstance(assessment, AssessmentRecord):
                action_id = assessment.action_id
            elif isinstance(assessment, dict):
                action_id = assessment.get("action_id", "unknown")

        record = EnforcementRecord(
            enforcement_id=enforcement_id,
            action_id=action_id,
            timestamp=timestamp,
            decision=decision,
            reason=reason,
            assessment_id=assessment_id,
            gate_status=gate_status,
            gl7_approved=gl7_approved,
            gl7_aborts=gl7_aborts if gl7_aborts else [],
        )

        return {
            "decision": decision,
            "reason": reason,
            "enforcement_id": enforcement_id,
            "action_id": action_id,
            "timestamp": timestamp,
            "details": {
                "a_ok": a_ok,
                "u_ok": u_ok,
                "r_ok": r_ok,
                "assessment_id": assessment_id,
                "confidence": confidence,
                "gate_status": gate_status,
                "gl7_approved": gl7_approved,
                "gl7_aborts": gl7_aborts if gl7_aborts else [],
            },
            "record": record,
        }

    def _check_assessment(self, assessment) -> tuple[bool, str, Optional[str], Optional[float]]:
        """Check Assessment condition (A)."""
        if assessment is None:
            return False, "assessment is None (fail-closed)", None, None

        if isinstance(assessment, dict):
            admissible = assessment.get("admissible", False)
            confidence = assessment.get("confidence", 0.0)
            assessment_id = assessment.get("assessment_id")
        elif isinstance(assessment, AssessmentRecord):
            admissible = assessment.admissible
            confidence = assessment.confidence
            assessment_id = assessment.assessment_id
        else:
            return False, f"unknown assessment type: {type(assessment)}", None, None

        if not admissible:
            return False, f"assessment inadmissible (confidence={confidence:.2f})", assessment_id, confidence

        if confidence < CONFIDENCE_THRESHOLD:
            return (
                False,
                f"confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}",
                assessment_id,
                confidence,
            )

        return True, "assessment admissible", assessment_id, confidence

    def _check_authorization(self, gate_result: Optional[dict]) -> tuple[bool, str, Optional[str]]:
        """Check Authorization condition (U). BA04 bypass prevention."""
        if gate_result is None:
            return False, "gate_result is None (BA04 bypass prevention)", None

        status = gate_result.get("status")
        if status is None:
            return False, "gate_result has no status field", None

        if status not in APPROVED_GATE_STATUSES:
            return False, f"Human Gate status={status} (must be APPROVED)", status

        return True, "Human Gate APPROVED", status

    def _check_runtime(self, gl7_result: Optional[dict]) -> tuple[bool, str, Optional[bool], list]:
        """Check Runtime Conformance condition (R)."""
        if gl7_result is None:
            return False, "gl7_result is None (fail-closed)", None, []

        approved = gl7_result.get("approved")
        aborts = gl7_result.get("aborts", [])

        if approved is None:
            return False, "gl7_result has no approved field", None, aborts

        if not approved:
            return False, f"GL7 dry run not approved; aborts={aborts}", False, aborts

        if aborts:
            return False, f"GL7 abort conditions present: {aborts}", approved, aborts

        return True, "GL7 runtime conformant", True, []
