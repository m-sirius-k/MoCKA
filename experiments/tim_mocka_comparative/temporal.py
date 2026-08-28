"""Re-evaluation gate over a past decision.

Model
-----
A past decision is not stored as a verdict to be replayed. It is stored as a
verdict PLUS the conditions under which it was reached, so that those
conditions can be re-checked against the present.

    DecisionRecord   what was decided, and on what premises
    PresentContext   what is true now
    ReEvaluationGate compares the two and reports eligibility

Eligibility is not a decision. It answers only "may the past decision be
reused as-is", and reuse of a past BLOCK is still a BLOCK.

Vocabulary in this module is LOCAL TO THIS EXPERIMENT. None of it is proposed
as a formal MoCKA primitive.
"""

import hashlib
from datetime import datetime, timezone
from enum import Enum


class PastDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class Eligibility(str, Enum):
    """May the past decision be reused as-is?"""

    ELIGIBLE = "ELIGIBLE"
    RE_EVALUATE = "RE_EVALUATE"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class Execution(str, Enum):
    EXECUTE = "EXECUTE"
    STOP = "STOP"


class Weight(str, Enum):
    """How a finding contributes to eligibility."""

    HARD_BLOCK = "HARD_BLOCK"
    REQUIRE_REEVALUATION = "REQUIRE_REEVALUATION"
    MAINTAIN_UNKNOWN = "MAINTAIN_UNKNOWN"
    INFORMATIONAL = "INFORMATIONAL"


# Local finding vocabulary. Experiment-scoped, not a primitive set.
_VOCAB = {
    "PREMISES_UNCHANGED": Weight.INFORMATIONAL,
    "TEMPORAL_EXPIRED": Weight.REQUIRE_REEVALUATION,
    "AUTHORITY_REVOKED": Weight.HARD_BLOCK,
    "AUTHORITY_CHANGED": Weight.REQUIRE_REEVALUATION,
    "EVIDENCE_CHANGED": Weight.REQUIRE_REEVALUATION,
    "CONTEXT_CHANGED": Weight.REQUIRE_REEVALUATION,
    "CONTEXT_MISMATCH": Weight.REQUIRE_REEVALUATION,
    "NO_NEW_EVIDENCE": Weight.MAINTAIN_UNKNOWN,
    "NEW_EVIDENCE_PRESENT": Weight.REQUIRE_REEVALUATION,
}


def digest(value):
    """Stable digest of an evidence or context payload."""
    return hashlib.sha256(repr(value).encode("utf-8")).hexdigest()[:16]


class Finding(object):
    __slots__ = ("name", "weight", "field", "detail")

    def __init__(self, name, field, detail):
        self.name = name
        self.weight = _VOCAB[name]
        self.field = field
        self.detail = detail

    def as_dict(self):
        return {
            "finding": self.name,
            "weight": self.weight.value,
            "field": self.field,
            "detail": self.detail,
        }

    def __repr__(self):
        return "Finding(%s)" % self.name


class DecisionRecord(object):
    """A past decision plus the premises it rested on."""

    __slots__ = (
        "decision_id",
        "decision",
        "decided_at",
        "validity_until",
        "evidence_digest",
        "authority_id",
        "context_id",
        "context_digest",
    )

    def __init__(
        self,
        decision_id,
        decision,
        decided_at,
        validity_until,
        evidence_digest,
        authority_id,
        context_id,
        context_digest,
    ):
        self.decision_id = decision_id
        self.decision = decision
        self.decided_at = decided_at
        self.validity_until = validity_until
        self.evidence_digest = evidence_digest
        self.authority_id = authority_id
        self.context_id = context_id
        self.context_digest = context_digest

    def as_dict(self):
        return {
            "decision_id": self.decision_id,
            "decision": self.decision.value,
            "decided_at": self.decided_at,
            "validity_until": self.validity_until,
            "evidence_digest": self.evidence_digest,
            "authority_id": self.authority_id,
            "context_id": self.context_id,
            "context_digest": self.context_digest,
        }


class PresentContext(object):
    """What is true now."""

    __slots__ = (
        "now",
        "evidence_digest",
        "authority_id",
        "authority_state",
        "context_id",
        "context_digest",
    )

    def __init__(
        self,
        now,
        evidence_digest,
        authority_id,
        authority_state,
        context_id,
        context_digest,
    ):
        self.now = now
        self.evidence_digest = evidence_digest
        self.authority_id = authority_id
        self.authority_state = authority_state
        self.context_id = context_id
        self.context_digest = context_digest

    def as_dict(self):
        return {
            "now": self.now,
            "evidence_digest": self.evidence_digest,
            "authority_id": self.authority_id,
            "authority_state": self.authority_state,
            "context_id": self.context_id,
            "context_digest": self.context_digest,
        }


class Assessment(object):
    __slots__ = ("eligibility", "execution", "findings", "record", "present", "reason")

    def __init__(self, eligibility, execution, findings, record, present, reason):
        self.eligibility = eligibility
        self.execution = execution
        self.findings = findings
        self.record = record
        self.present = present
        self.reason = reason

    @property
    def finding_names(self):
        return [f.name for f in self.findings]

    def as_dict(self):
        return {
            "eligibility": self.eligibility.value,
            "execution": self.execution.value,
            "findings": [f.as_dict() for f in self.findings],
            "reason": self.reason,
            "past_decision": self.record.decision.value,
            "record": self.record.as_dict(),
            "present": self.present.as_dict(),
        }


def _parse(ts):
    text = ts[:-1] + "+00:00" if ts.endswith("Z") else ts
    return datetime.fromisoformat(text)


def reduce_eligibility(findings, past_decision):
    """Reduce findings to an eligibility.

    HARD_BLOCK           -> BLOCK
    REQUIRE_REEVALUATION -> RE_EVALUATE
    past decision UNKNOWN and nothing above -> UNKNOWN (it stays unknown)
    otherwise            -> ELIGIBLE
    """
    if any(f.weight is Weight.HARD_BLOCK for f in findings):
        return Eligibility.BLOCK
    if any(f.weight is Weight.REQUIRE_REEVALUATION for f in findings):
        return Eligibility.RE_EVALUATE
    if past_decision is PastDecision.UNKNOWN:
        return Eligibility.UNKNOWN
    return Eligibility.ELIGIBLE


def gate_execution(eligibility, past_decision):
    """Only a reusable past ALLOW executes.

    Every other combination stops. In particular a reusable past BLOCK is still
    a stop, and RE_EVALUATE and UNKNOWN never execute.
    """
    if not isinstance(eligibility, Eligibility) or not isinstance(past_decision, PastDecision):
        return Execution.STOP
    if eligibility is Eligibility.ELIGIBLE and past_decision is PastDecision.ALLOW:
        return Execution.EXECUTE
    return Execution.STOP


class ReEvaluationGate(object):
    """Compares a stored decision record against the present."""

    def assess(self, record, present):
        findings = []

        if record.context_id != present.context_id:
            findings.append(
                Finding(
                    "CONTEXT_MISMATCH",
                    "context_id",
                    "record was made for context %s, present context is %s"
                    % (record.context_id, present.context_id),
                )
            )
        elif record.context_digest != present.context_digest:
            findings.append(
                Finding(
                    "CONTEXT_CHANGED",
                    "context_digest",
                    "same context id, but its content changed",
                )
            )

        if present.authority_state in ("LOST", "REVOKED"):
            findings.append(
                Finding(
                    "AUTHORITY_REVOKED",
                    "authority_state",
                    "authority_state=%s at present" % present.authority_state,
                )
            )
        elif record.authority_id != present.authority_id:
            findings.append(
                Finding(
                    "AUTHORITY_CHANGED",
                    "authority_id",
                    "decision was made under %s, present authority is %s"
                    % (record.authority_id, present.authority_id),
                )
            )

        if _parse(present.now) > _parse(record.validity_until):
            findings.append(
                Finding(
                    "TEMPORAL_EXPIRED",
                    "validity_until",
                    "validity ended %s, now is %s" % (record.validity_until, present.now),
                )
            )

        if record.evidence_digest != present.evidence_digest:
            if record.decision is PastDecision.UNKNOWN:
                findings.append(
                    Finding(
                        "NEW_EVIDENCE_PRESENT",
                        "evidence_digest",
                        "evidence changed since an UNKNOWN decision",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "EVIDENCE_CHANGED",
                        "evidence_digest",
                        "evidence differs from the evidence the decision rested on",
                    )
                )
        elif record.decision is PastDecision.UNKNOWN:
            findings.append(
                Finding(
                    "NO_NEW_EVIDENCE",
                    "evidence_digest",
                    "no new evidence since the UNKNOWN decision",
                )
            )

        if not findings:
            findings.append(
                Finding("PREMISES_UNCHANGED", None, "all recorded premises still hold")
            )

        eligibility = reduce_eligibility(findings, record.decision)
        execution = gate_execution(eligibility, record.decision)

        if eligibility is Eligibility.ELIGIBLE:
            reason = "premises unchanged; past %s may be reused" % record.decision.value
        elif eligibility is Eligibility.BLOCK:
            reason = "hard block: %s" % ", ".join(
                f.name for f in findings if f.weight is Weight.HARD_BLOCK
            )
        elif eligibility is Eligibility.UNKNOWN:
            reason = "past decision was UNKNOWN and nothing new arrived"
        else:
            reason = "re-evaluation required: %s" % ", ".join(
                f.name for f in findings if f.weight is Weight.REQUIRE_REEVALUATION
            )

        return Assessment(eligibility, execution, findings, record, present, reason)


def reuse_directly(record):
    """ANTI-PATTERN, included as a control. Do not treat its output as a decision.

    This is the path the experiment exists to argue against: taking the stored
    verdict and replaying it with no reference to the present at all. It is
    implemented so the two paths can be compared side by side, and its ALLOW is
    never counted as a legitimate ALLOW.
    """
    return record.decision
