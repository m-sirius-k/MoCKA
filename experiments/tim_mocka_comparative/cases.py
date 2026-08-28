"""Case matrix T01-T10 plus the central reuse comparison.

The matrix is taken verbatim from the commissioning instruction (its Minimum
Test Matrix and Critical Test sections). It is not derived from, and does not
model, any external party's stated position; no such material was supplied to
this session. See docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md.

Scoring axes, per the instruction, are scored PASS / FAIL / UNKNOWN /
NOT_TESTED. UNKNOWN is never counted as FAIL.
"""

from .temporal import DecisionRecord, PastDecision, PresentContext, digest

# Fixed clock, so every run is reproducible.
NOW = "2026-08-28T12:00:00Z"
DECIDED_AT = "2026-08-01T00:00:00Z"
VALID_FUTURE = "2026-09-30T00:00:00Z"
VALID_PAST = "2026-08-10T00:00:00Z"

EV_ORIGINAL = digest("evidence-set-A")
EV_CHANGED = digest("evidence-set-B")
CTX_ORIGINAL = digest("context-payload-1")
CTX_CHANGED = digest("context-payload-1-revised")

AUTH_ORIGINAL = "AUTH-OPERATOR-01"
AUTH_OTHER = "AUTH-OPERATOR-02"
CTX_ID = "CTX-1"
CTX_ID_OTHER = "CTX-2"

# Axis names and the finding vocabulary each axis owns.
AXES = (
    "evidence_preservation",
    "temporal_validity",
    "authority_continuity",
    "context_continuity",
    "re_evaluation_correctness",
)

AXIS_VOCAB = {
    "evidence_preservation": {"EVIDENCE_CHANGED", "NEW_EVIDENCE_PRESENT", "NO_NEW_EVIDENCE"},
    "temporal_validity": {"TEMPORAL_EXPIRED"},
    "authority_continuity": {"AUTHORITY_REVOKED", "AUTHORITY_CHANGED"},
    "context_continuity": {"CONTEXT_MISMATCH", "CONTEXT_CHANGED"},
}

NOT_TESTED = "NOT_TESTED"
UNKNOWN_AXIS = "UNKNOWN"


def record(decision, validity_until=VALID_FUTURE, evidence=EV_ORIGINAL,
           authority=AUTH_ORIGINAL, context_id=CTX_ID, context_digest=CTX_ORIGINAL,
           decision_id="D-0001"):
    return DecisionRecord(
        decision_id=decision_id,
        decision=decision,
        decided_at=DECIDED_AT,
        validity_until=validity_until,
        evidence_digest=evidence,
        authority_id=authority,
        context_id=context_id,
        context_digest=context_digest,
    )


def present(evidence=EV_ORIGINAL, authority=AUTH_ORIGINAL, authority_state="VALID",
            context_id=CTX_ID, context_digest=CTX_ORIGINAL, now=NOW):
    return PresentContext(
        now=now,
        evidence_digest=evidence,
        authority_id=authority,
        authority_state=authority_state,
        context_id=context_id,
        context_digest=context_digest,
    )


def expected_findings(case):
    """The exact finding set a case should produce, plus the axes left open.

    An axis a case does not vary is NOT_TESTED, so it contributes nothing and
    must stay silent. An axis scored UNKNOWN is left open: its vocabulary is
    returned separately so the caller can exclude it from exact matching
    instead of guessing.
    """
    expected = set()
    open_vocab = set()
    for axis, declared in case.axes.items():
        if declared == NOT_TESTED:
            continue
        if declared == UNKNOWN_AXIS:
            open_vocab |= AXIS_VOCAB[axis]
            continue
        expected |= set(declared)
    if not expected and not open_vocab:
        expected = {"PREMISES_UNCHANGED"}
    return expected, open_vocab


def findings_match(case, actual_names):
    """True when the gate raised exactly what the case declared, no more.

    This is the false-positive guard. Because NOT_TESTED axes no longer assert
    absence individually, the guard is applied once over the whole finding set.
    """
    expected, open_vocab = expected_findings(case)
    actual = set(actual_names) - open_vocab
    return actual == (expected - open_vocab)


class Case(object):
    __slots__ = ("case_id", "past", "now_state", "record", "present", "expected_eligibility",
                 "expected_execution", "axes", "note")

    def __init__(self, case_id, past, now_state, rec, pres, expected_eligibility,
                 expected_execution, axes, note=""):
        self.case_id = case_id
        self.past = past
        self.now_state = now_state
        self.record = rec
        self.present = pres
        self.expected_eligibility = tuple(expected_eligibility)
        self.expected_execution = expected_execution
        self.axes = axes
        self.note = note


CASES = [
    Case(
        "T01", "Allow", "premises unchanged",
        record(PastDecision.ALLOW), present(),
        ("ELIGIBLE",), "EXECUTE",
        {
            "evidence_preservation": NOT_TESTED,
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
        note="Control. Varies nothing, so no axis is exercised. If nothing may "
             "ever be reused, the gate proves nothing.",
    ),
    Case(
        "T02", "Allow", "validity expired",
        record(PastDecision.ALLOW, validity_until=VALID_PAST), present(),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": NOT_TESTED,
            "temporal_validity": {"TEMPORAL_EXPIRED"},
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
    ),
    Case(
        "T03", "Allow", "authority revoked",
        record(PastDecision.ALLOW), present(authority_state="REVOKED"),
        ("BLOCK", "RE_EVALUATE"), "STOP",
        {
            "evidence_preservation": NOT_TESTED,
            "temporal_validity": NOT_TESTED,
            "authority_continuity": {"AUTHORITY_REVOKED"},
            "context_continuity": NOT_TESTED,
        },
    ),
    Case(
        "T04", "Allow", "evidence changed",
        record(PastDecision.ALLOW), present(evidence=EV_CHANGED),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": {"EVIDENCE_CHANGED"},
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
    ),
    Case(
        "T05", "Allow", "context content changed",
        record(PastDecision.ALLOW), present(context_digest=CTX_CHANGED),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": NOT_TESTED,
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": {"CONTEXT_CHANGED"},
        },
    ),
    Case(
        "T06", "Block", "premises unchanged",
        record(PastDecision.BLOCK), present(),
        ("ELIGIBLE",), "STOP",
        {
            "evidence_preservation": NOT_TESTED,
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
        note="Reusable does not mean permitted. A reusable BLOCK still stops.",
    ),
    Case(
        "T07", "Block", "state improved",
        record(PastDecision.BLOCK), present(evidence=EV_CHANGED),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": {"EVIDENCE_CHANGED"},
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
        note="Improvement must not auto-lift a BLOCK. Whether re-evaluation would "
             "now allow it is outside this gate.",
    ),
    Case(
        "T08", "UNKNOWN", "no new evidence",
        record(PastDecision.UNKNOWN), present(),
        ("UNKNOWN",), "STOP",
        {
            "evidence_preservation": {"NO_NEW_EVIDENCE"},
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
    ),
    Case(
        "T09", "UNKNOWN", "new evidence present",
        record(PastDecision.UNKNOWN), present(evidence=EV_CHANGED),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": {"NEW_EVIDENCE_PRESENT"},
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": NOT_TESTED,
        },
    ),
    Case(
        "T10", "Allow (reused)", "context mismatch",
        record(PastDecision.ALLOW), present(context_id=CTX_ID_OTHER),
        ("RE_EVALUATE",), "STOP",
        {
            "evidence_preservation": UNKNOWN_AXIS,
            "temporal_validity": NOT_TESTED,
            "authority_continuity": NOT_TESTED,
            "context_continuity": {"CONTEXT_MISMATCH"},
        },
        note="Evidence preservation is UNKNOWN here: the digests are comparable "
             "mechanically, but whether comparing evidence across a context "
             "boundary is meaningful is not determinable within this experiment.",
    ),
]


# --- Critical test: past decision reused directly vs re-evaluated -----------
#
# Path A replays the stored verdict with no reference to the present.
# Path B runs the same record through the re-evaluation gate.
# The premises have changed in every way the gate can see, so if A yields ALLOW
# it is an unearned ALLOW, not a passing result.

T50_RECORD = record(
    PastDecision.ALLOW,
    validity_until=VALID_PAST,
    evidence=EV_ORIGINAL,
    authority=AUTH_ORIGINAL,
    context_id=CTX_ID,
    context_digest=CTX_ORIGINAL,
    decision_id="D-T50",
)

T50_PRESENT = present(
    evidence=EV_CHANGED,
    authority=AUTH_OTHER,
    context_id=CTX_ID_OTHER,
    context_digest=CTX_CHANGED,
)

T50_EXPECTED = {
    "A": {
        "description": "Past Decision reused directly (anti-pattern control)",
        "expected_output": "ALLOW",
        "legitimacy": "NOT A LEGITIMATE ALLOW",
        "axes": {axis: "FAIL" for axis in AXES},
        "note": "Path A performs no comparison against the present at all, so it "
                "fails every axis by construction. Its ALLOW is recorded as an "
                "unearned output, never as evidence of eligibility.",
    },
    "B": {
        "description": "Past Decision + current re-evaluation",
        "expected_eligibility": ("RE_EVALUATE", "BLOCK"),
        "expected_execution": "STOP",
        "note": "Path B must re-check evidence, temporal validity, authority and "
                "context before any reuse.",
    },
}
