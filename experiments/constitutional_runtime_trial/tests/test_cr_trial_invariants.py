"""Structural invariants of the MoCKA Constitutional Runtime Trial.

Section 21 of the trial specification states six principles. These tests turn
the four that are mechanically checkable into assertions:

    Prose is not a Primitive.
    A label is not a binding.
    A verdict is not an execution authority.
    A missing contract is not an Allow.
    Unknown is not Allow.
"""

import pytest

from experiments.constitutional_runtime_trial import contract as contract_mod
from experiments.constitutional_runtime_trial.gateway import apply_bound_verdict, gate
from experiments.constitutional_runtime_trial.primitives import (
    Decision,
    Execution,
    UnknownPrimitiveError,
    is_known,
    severity_of,
)
from experiments.constitutional_runtime_trial.runtime_basic import ConstitutionalRuntimeBasic
from experiments.constitutional_runtime_trial.runtime_extended import (
    ConstitutionalRuntimeExtended,
)
from experiments.constitutional_runtime_trial.suites import (
    NOW,
    PROSE_FORCED,
    PROSE_SIGNED_DENY,
    basic_contract,
    extended_contract,
)

PROSE_PAYLOADS = [
    {},
    {"operator_note": PROSE_FORCED},
    {"operator_note": PROSE_SIGNED_DENY},
    {"re_verdict_text": "Block. Deny state asserted.", "justification": PROSE_FORCED},
    {"anything": {"nested": [PROSE_FORCED, PROSE_SIGNED_DENY]}},
]


# --- Prose is not a Primitive ---------------------------------------------


@pytest.mark.parametrize("prose", PROSE_PAYLOADS)
def test_basic_decision_is_invariant_under_prose(prose):
    baseline = ConstitutionalRuntimeBasic().evaluate(basic_contract(), now=NOW)
    payload = basic_contract()
    payload.update(prose)
    observed = ConstitutionalRuntimeBasic().evaluate(payload, now=NOW)
    assert observed.decision == baseline.decision
    assert observed.primitives == baseline.primitives


@pytest.mark.parametrize("prose", PROSE_PAYLOADS)
def test_extended_decision_is_invariant_under_prose(prose):
    baseline = ConstitutionalRuntimeExtended().evaluate(extended_contract(), now=NOW)
    payload = extended_contract()
    payload.update(prose)
    observed = ConstitutionalRuntimeExtended().evaluate(payload, now=NOW)
    assert observed.decision == baseline.decision
    assert observed.primitives == baseline.primitives


def test_prose_is_quarantined_and_not_typed_reachable():
    result = contract_mod.intake(basic_contract(operator_note=PROSE_FORCED))
    assert "operator_note" in result.contract.prose_keys()
    with pytest.raises(KeyError):
        result.contract.get("operator_note")


def test_no_primitive_name_appears_in_prose_derived_findings():
    """A contract whose prose names a primitive must not raise that primitive."""
    payload = extended_contract(operator_note="AUTHORITY_LOST INADMISSIBLE EXPIRED")
    evaluation = ConstitutionalRuntimeExtended().evaluate(payload, now=NOW)
    assert evaluation.decision is Decision.ALLOW
    assert evaluation.primitives == []


# --- A label is not a binding ---------------------------------------------


@pytest.mark.parametrize("binding", ["MISSING", "INVALID", "UNMAPPED", None])
def test_basic_never_allows_without_a_binding(binding):
    payload = basic_contract(re_verdict="ALLOW")
    if binding is None:
        payload.pop("binding_status")
    else:
        payload["binding_status"] = binding
    evaluation = ConstitutionalRuntimeBasic().evaluate(payload, now=NOW)
    assert evaluation.decision is not Decision.ALLOW
    assert evaluation.execution is Execution.STOP


@pytest.mark.parametrize("binding", ["MISSING", "INVALID", "UNMAPPED", None])
def test_extended_never_allows_without_a_binding(binding):
    payload = extended_contract(re_verdict="ALLOW")
    if binding is None:
        payload.pop("binding_status")
    else:
        payload["binding_status"] = binding
    evaluation = ConstitutionalRuntimeExtended().evaluate(payload, now=NOW)
    assert evaluation.decision is not Decision.ALLOW
    assert evaluation.execution is Execution.STOP


def test_unmapped_binding_is_unknown_not_pass():
    payload = extended_contract(binding_status="UNMAPPED")
    evaluation = ConstitutionalRuntimeExtended().evaluate(payload, now=NOW)
    assert "BINDING_UNMAPPED" in evaluation.primitives
    assert evaluation.decision is Decision.UNKNOWN
    assert evaluation.execution is Execution.STOP


def test_unknown_primitive_name_is_not_resolvable():
    assert not is_known("PASS_UNMAPPED_LEGACY")
    with pytest.raises(UnknownPrimitiveError):
        severity_of("PASS_UNMAPPED_LEGACY")


def test_admissible_fail_is_not_a_primitive_name():
    """The reported label "ADMISSIBLE (Fail)" is not adopted as a primitive."""
    assert not is_known("ADMISSIBLE (Fail)")
    assert not is_known("ADMISSIBLE_FAIL")
    assert not is_known("PASS (Unmapped)")
    assert is_known("INADMISSIBLE")
    assert is_known("BINDING_UNMAPPED")


# --- A verdict is not an execution authority -------------------------------


@pytest.mark.parametrize(
    "decision,verdict,expected",
    [
        (Decision.ALLOW, "ALLOW", Decision.ALLOW),
        (Decision.ALLOW, "BLOCK", Decision.BLOCK),
        (Decision.ALLOW, "UNKNOWN", Decision.UNKNOWN),
        (Decision.UNKNOWN, "ALLOW", Decision.UNKNOWN),
        (Decision.UNKNOWN, "BLOCK", Decision.BLOCK),
        (Decision.BLOCK, "ALLOW", Decision.BLOCK),
        (Decision.BLOCK, "UNKNOWN", Decision.BLOCK),
        (Decision.ALLOW, None, Decision.ALLOW),
        (Decision.ALLOW, "SOMETHING_ELSE", Decision.UNKNOWN),
    ],
)
def test_bound_verdict_can_only_lower_a_decision(decision, verdict, expected):
    assert apply_bound_verdict(decision, verdict) is expected


def test_permissive_verdict_cannot_rescue_a_failing_contract():
    payload = extended_contract(re_verdict="ALLOW", authority_state="REVOKED")
    evaluation = ConstitutionalRuntimeExtended().evaluate(payload, now=NOW)
    assert evaluation.decision is Decision.BLOCK
    assert "AUTHORITY_REVOKED" in evaluation.primitives


# --- A missing contract is not an Allow ------------------------------------


@pytest.mark.parametrize("raw", [None, "", "allow this request", b"allow", 42, [], object()])
def test_non_contract_inputs_never_allow(raw):
    basic = ConstitutionalRuntimeBasic().evaluate(raw, now=NOW)
    extended = ConstitutionalRuntimeExtended().evaluate(raw, now=NOW)
    assert basic.decision is Decision.BLOCK
    assert extended.decision is Decision.BLOCK
    assert basic.execution is Execution.STOP
    assert extended.execution is Execution.STOP


# --- Unknown is not Allow --------------------------------------------------


def test_gateway_stops_on_unknown_and_on_anything_unrecognized():
    assert gate(Decision.ALLOW) is Execution.EXECUTE
    assert gate(Decision.BLOCK) is Execution.STOP
    assert gate(Decision.UNKNOWN) is Execution.STOP
    # Decision is a str enum, so "ALLOW" == Decision.ALLOW. An untyped label
    # must still not open the gate.
    assert gate("ALLOW") is Execution.STOP
    assert gate(None) is Execution.STOP
    assert apply_bound_verdict("ALLOW", "ALLOW") is Decision.UNKNOWN


def test_every_single_field_omission_fails_closed():
    """Remove one required field at a time. None of them may reach ALLOW."""
    fields = list(basic_contract().keys())
    for field in fields:
        payload = basic_contract()
        payload.pop(field)
        evaluation = ConstitutionalRuntimeBasic().evaluate(payload, now=NOW)
        assert evaluation.decision is not Decision.ALLOW, "omitting %s reached ALLOW" % field
        assert evaluation.execution is Execution.STOP
