# test_decision_synthesis.py
"""STEP 2: DecisionSynthesis 検証"""
from phios.core.event_interpreter import InterpretedEvent
from phios.core.decision_synthesis import DecisionSynthesizer, Action


def test_synthesize_critical_escalates_to_human_gate():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.action_type == "escalate"
    assert action.target == "human_gate"


def test_synthesize_recover_delegates_to_mock():
    event = InterpretedEvent("STATE_DEGRADED", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.action_type == "delegate"
    assert action.target == "mock"


def test_synthesize_validate_seals_via_verify_all():
    event = InterpretedEvent("SEAL", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.action_type == "seal"
    assert action.target == "verify_all"


def test_synthesize_default_is_noop():
    event = InterpretedEvent("STATE_INIT", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.action_type == "noop"
    assert action.target == "ledger"


def test_synthesize_priority_uses_urgency():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.priority == 3


def test_synthesize_reason_format():
    event = InterpretedEvent("SEAL", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.reason == "seal:SEAL"


def test_action_is_plain_object():
    action = Action("noop", "ledger", 1, "noop:TEST")
    assert action.action_type == "noop"
    assert action.target == "ledger"
    assert action.priority == 1
    assert action.reason == "noop:TEST"
