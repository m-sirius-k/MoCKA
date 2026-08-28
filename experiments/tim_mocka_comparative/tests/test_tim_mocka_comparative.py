"""Invariants for the re-evaluation gate.

These are separate from the Constitutional Runtime Trial suite. That suite's
117 tests and 24 cases are the frozen regression baseline and are not touched
here.
"""

import itertools

import pytest

from experiments.tim_mocka_comparative.cases import (
    AUTH_ORIGINAL,
    AUTH_OTHER,
    CASES,
    CTX_CHANGED,
    CTX_ID,
    CTX_ID_OTHER,
    CTX_ORIGINAL,
    EV_CHANGED,
    EV_ORIGINAL,
    T50_PRESENT,
    T50_RECORD,
    VALID_FUTURE,
    VALID_PAST,
    findings_match,
    present,
    record,
)
from experiments.tim_mocka_comparative.run_comparative import run_matrix, run_t50, score_axes
from experiments.tim_mocka_comparative.temporal import (
    Eligibility,
    Execution,
    PastDecision,
    ReEvaluationGate,
    gate_execution,
    reuse_directly,
)

GATE = ReEvaluationGate()


# --- the declared matrix ---------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=[c.case_id for c in CASES])
def test_case_matches_expectation(case):
    a = GATE.assess(case.record, case.present)
    assert a.eligibility.value in case.expected_eligibility, (
        "%s expected %s, got %s (%s)"
        % (case.case_id, case.expected_eligibility, a.eligibility.value, a.reason)
    )
    assert a.execution.value == case.expected_execution


@pytest.mark.parametrize("case", CASES, ids=[c.case_id for c in CASES])
def test_only_the_control_case_executes(case):
    a = GATE.assess(case.record, case.present)
    if case.case_id == "T01":
        assert a.execution is Execution.EXECUTE
    else:
        assert a.execution is Execution.STOP, "%s reached execution" % case.case_id


@pytest.mark.parametrize("case", CASES, ids=[c.case_id for c in CASES])
def test_no_spurious_findings(case):
    """False-positive guard.

    An axis a case does not vary must stay silent. Since NOT_TESTED axes no
    longer assert absence one by one, the guard is applied over the whole
    finding set instead.
    """
    a = GATE.assess(case.record, case.present)
    assert findings_match(case, a.finding_names), (
        "%s raised %s, which is not what it declared" % (case.case_id, a.finding_names)
    )


def test_axis_tally_reflects_variation_not_mere_passing():
    """Each axis should be scored PASS only by the cases that vary it."""
    rows = run_matrix()
    tally = {}
    for row in rows:
        for axis, score in row["axis_scores"].items():
            tally.setdefault(axis, {}).setdefault(score, 0)
            tally[axis][score] += 1
    assert tally["temporal_validity"]["PASS"] == 1
    assert tally["authority_continuity"]["PASS"] == 1
    assert tally["context_continuity"]["PASS"] == 2
    assert tally["evidence_preservation"]["PASS"] == 4
    assert tally["evidence_preservation"]["UNKNOWN"] == 1
    assert tally["re_evaluation_correctness"]["PASS"] == 10


def test_unknown_axis_is_never_scored_as_fail():
    """The instruction forbids collapsing UNKNOWN into FAIL."""
    t10 = next(c for c in CASES if c.case_id == "T10")
    scores = score_axes(t10, GATE.assess(t10.record, t10.present))
    assert scores["evidence_preservation"] == "UNKNOWN"


# --- the core principle ----------------------------------------------------


def test_past_allow_alone_never_grants_execution():
    """A past ALLOW must not carry itself into the present.

    Every single-premise change is enough to stop it.
    """
    changes = [
        ("expired", record(PastDecision.ALLOW, validity_until=VALID_PAST), present()),
        ("evidence", record(PastDecision.ALLOW), present(evidence=EV_CHANGED)),
        ("authority revoked", record(PastDecision.ALLOW), present(authority_state="REVOKED")),
        ("authority changed", record(PastDecision.ALLOW), present(authority=AUTH_OTHER)),
        ("context content", record(PastDecision.ALLOW), present(context_digest=CTX_CHANGED)),
        ("context identity", record(PastDecision.ALLOW), present(context_id=CTX_ID_OTHER)),
    ]
    for label, rec, pres in changes:
        a = GATE.assess(rec, pres)
        assert a.execution is Execution.STOP, "%s still executed" % label
        assert a.eligibility is not Eligibility.ELIGIBLE, "%s stayed eligible" % label


def test_reusable_block_is_still_a_stop():
    a = GATE.assess(record(PastDecision.BLOCK), present())
    assert a.eligibility is Eligibility.ELIGIBLE
    assert a.execution is Execution.STOP


def test_improved_state_does_not_lift_a_block():
    a = GATE.assess(record(PastDecision.BLOCK), present(evidence=EV_CHANGED))
    assert a.eligibility is Eligibility.RE_EVALUATE
    assert a.execution is Execution.STOP


def test_unknown_stays_unknown_without_new_evidence():
    a = GATE.assess(record(PastDecision.UNKNOWN), present())
    assert a.eligibility is Eligibility.UNKNOWN
    assert a.execution is Execution.STOP


def test_unknown_with_new_evidence_requires_re_evaluation():
    a = GATE.assess(record(PastDecision.UNKNOWN), present(evidence=EV_CHANGED))
    assert a.eligibility is Eligibility.RE_EVALUATE
    assert a.execution is Execution.STOP


# --- exhaustive check ------------------------------------------------------


def test_exhaustive_only_unchanged_past_allow_executes():
    """288 combinations. Execution requires a past ALLOW and every premise intact."""
    executed = []
    total = 0
    for past, ev, valid, astate, aid, cid, cdig in itertools.product(
        (PastDecision.ALLOW, PastDecision.BLOCK, PastDecision.UNKNOWN),
        (EV_ORIGINAL, EV_CHANGED),
        (VALID_FUTURE, VALID_PAST),
        ("VALID", "LOST", "REVOKED"),
        (AUTH_ORIGINAL, AUTH_OTHER),
        (CTX_ID, CTX_ID_OTHER),
        (CTX_ORIGINAL, CTX_CHANGED),
    ):
        total += 1
        a = GATE.assess(
            record(past, validity_until=valid),
            present(evidence=ev, authority=aid, authority_state=astate,
                    context_id=cid, context_digest=cdig),
        )
        if a.execution is Execution.EXECUTE:
            executed.append((past.value, ev, valid, astate, aid, cid, cdig))
        if a.eligibility in (Eligibility.RE_EVALUATE, Eligibility.UNKNOWN, Eligibility.BLOCK):
            assert a.execution is Execution.STOP

    assert total == 288
    assert executed == [
        (
            PastDecision.ALLOW.value,
            EV_ORIGINAL,
            VALID_FUTURE,
            "VALID",
            AUTH_ORIGINAL,
            CTX_ID,
            CTX_ORIGINAL,
        )
    ], "unexpected execution paths: %s" % executed


# --- the anti-pattern control ---------------------------------------------


def test_direct_reuse_ignores_the_present_entirely():
    """Path A returns the stored verdict no matter what the present says."""
    assert reuse_directly(T50_RECORD) is PastDecision.ALLOW
    unrelated = present(evidence=EV_CHANGED, authority_state="REVOKED",
                        context_id=CTX_ID_OTHER, context_digest=CTX_CHANGED)
    assert reuse_directly(T50_RECORD) is PastDecision.ALLOW
    assert GATE.assess(T50_RECORD, unrelated).execution is Execution.STOP


def test_t50_paths_diverge():
    t50 = run_t50()
    assert t50["path_A"]["output"] == "ALLOW"
    assert t50["path_A"]["comparisons_performed"] == 0
    assert t50["path_A"]["legitimacy"] == "NOT A LEGITIMATE ALLOW"
    assert all(v == "FAIL" for v in t50["path_A"]["axis_scores"].values())
    assert t50["path_B"]["execution"] == "STOP"
    assert set(t50["path_B"]["findings"]) == {
        "CONTEXT_MISMATCH",
        "AUTHORITY_CHANGED",
        "TEMPORAL_EXPIRED",
        "EVIDENCE_CHANGED",
    }


# --- type boundary ---------------------------------------------------------


def test_execution_gate_rejects_untyped_values():
    """Same str-enum hazard the CR trial hit. A label is not an eligibility."""
    assert gate_execution(Eligibility.ELIGIBLE, PastDecision.ALLOW) is Execution.EXECUTE
    assert gate_execution("ELIGIBLE", "ALLOW") is Execution.STOP
    assert gate_execution(Eligibility.ELIGIBLE, "ALLOW") is Execution.STOP
    assert gate_execution("ELIGIBLE", PastDecision.ALLOW) is Execution.STOP
    assert gate_execution(None, None) is Execution.STOP
    assert gate_execution(Eligibility.RE_EVALUATE, PastDecision.ALLOW) is Execution.STOP
    assert gate_execution(Eligibility.UNKNOWN, PastDecision.ALLOW) is Execution.STOP


# --- runner integrity ------------------------------------------------------


def test_runner_reports_all_cases_pass():
    rows = run_matrix()
    assert len(rows) == 10
    assert [r for r in rows if r["result"] == "FAIL"] == []
    assert [r["case_id"] for r in rows if r["execution_eligibility"] == "EXECUTE"] == ["T01"]
