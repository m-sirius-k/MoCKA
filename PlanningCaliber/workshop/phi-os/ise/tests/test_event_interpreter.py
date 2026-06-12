# test_event_interpreter.py
"""STEP 1: EventInterpreter 検証"""
from phios.core.event_interpreter import InterpretedEvent


def test_interpreter_seal():
    event = InterpretedEvent("SEAL", {"actor": "mocka-seal"})
    assert event.category == "audit"
    assert event.meaning["intent"] == "validate"


def test_interpreter_violation_is_critical_or_recover():
    event = InterpretedEvent("VIOLATION", {})
    assert event.meaning["intent"] == "recover"


def test_interpreter_state_change_is_system_impact():
    event = InterpretedEvent("STATE_CHANGE", {})
    assert event.meaning["impact"] == "system"


def test_interpreter_authority_revoke_is_critical():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    assert event.severity == "critical"
    assert event.meaning["impact"] == "critical"
    assert event.meaning["urgency"] == 3


def test_interpreter_unknown_event_defaults():
    event = InterpretedEvent("NOT_A_REAL_EVENT", {})
    assert event.category is None
    assert event.severity == "info"
    assert event.meaning["intent"] == "observe"


def test_interpreter_meaning_keys():
    event = InterpretedEvent("STATE_INIT", {})
    assert set(event.meaning.keys()) == {"intent", "impact", "urgency"}


def test_interpreter_raw_preserved():
    event = InterpretedEvent("STATE_INIT", {"actor": "Claude"})
    assert event.raw == {"actor": "Claude"}
