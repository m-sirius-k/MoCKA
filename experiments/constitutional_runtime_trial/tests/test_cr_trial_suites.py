"""Suite tests for the MoCKA Constitutional Runtime Trial.

These assert the specified expectations of every Basic, Extended, and Test 50
boundary case. The cases themselves live in suites.py so that this test run and
the published results document consume the same definitions.
"""

import pytest

from experiments.constitutional_runtime_trial.run_trial import evaluate_case
from experiments.constitutional_runtime_trial.suites import (
    ALL_CASES,
    BASIC_CASES,
    EXTENDED_CASES,
    TEST50_CASES,
)

CONTROL_CASES = {"B01", "E00"}


@pytest.mark.parametrize("case", ALL_CASES, ids=[c.test_id for c in ALL_CASES])
def test_case_decision_matches_specification(case):
    evaluation = evaluate_case(case)
    assert evaluation.decision.value in case.expected, (
        "%s expected %s, got %s (%s)"
        % (case.test_id, case.expected, evaluation.decision.value, evaluation.reason)
    )


@pytest.mark.parametrize("case", ALL_CASES, ids=[c.test_id for c in ALL_CASES])
def test_only_control_cases_reach_execution(case):
    evaluation = evaluate_case(case)
    if case.test_id in CONTROL_CASES:
        assert evaluation.execution.value == "EXECUTE"
    else:
        assert evaluation.execution.value == "STOP", (
            "%s reached execution; every non-control case must stop" % case.test_id
        )


@pytest.mark.parametrize("case", ALL_CASES, ids=[c.test_id for c in ALL_CASES])
def test_unknown_never_executes(case):
    evaluation = evaluate_case(case)
    if evaluation.decision.value == "UNKNOWN":
        assert evaluation.execution.value == "STOP"


def test_suite_sizes():
    """The specification asks for B01-B10, E01-E10 plus the E2E case, and the
    Test 50 boundary pair. E00 is a trial-added control."""
    assert len(BASIC_CASES) == 10
    assert len(EXTENDED_CASES) == 12
    assert len(TEST50_CASES) == 2


def test_b10_blocks_on_binding_not_on_verdict():
    """The decisive Basic case.

    B10 must block because the verdict is not bound, not because the runtime
    read the verdict. Proof: flipping the verdict to ALLOW keeps the block and
    keeps the same primitive.
    """
    b10 = next(c for c in BASIC_CASES if c.test_id == "B10")
    blocked = evaluate_case(b10)
    assert blocked.decision.value == "BLOCK"
    assert blocked.primitives == ["CONTRACT_INVALID"]
    assert blocked.findings[0].field == "binding_status"

    flipped = dict(b10.raw)
    flipped["re_verdict"] = "ALLOW"
    from experiments.constitutional_runtime_trial.runtime_basic import (
        ConstitutionalRuntimeBasic,
    )
    from experiments.constitutional_runtime_trial.suites import NOW

    other = ConstitutionalRuntimeBasic().evaluate(flipped, now=NOW)
    assert other.decision.value == "BLOCK"
    assert other.primitives == ["CONTRACT_INVALID"]


def test_test50_boundary_stops_in_both_runtimes():
    """The reported boundary was CR = Allow with Execution = CONTINUE.

    Both trial runtimes must stop on the same semantic input. This is a
    property of the trial design, not a statement about any pre-existing
    runtime.
    """
    for case in TEST50_CASES:
        evaluation = evaluate_case(case)
        assert evaluation.decision.value != "ALLOW"
        assert evaluation.execution.value == "STOP"
