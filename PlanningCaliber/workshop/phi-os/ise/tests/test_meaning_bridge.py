# test_meaning_bridge.py
"""STEP 5: meaning_bridge (Phase3 -> Phase4 接続) 検証"""
from phios.core.event_interpreter import InterpretedEvent
from phios.core.meaning_bridge import to_vector, from_vector
from phios.registry.taxonomy import get_taxonomy


def test_to_vector_critical_event():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    vector = to_vector(event)
    assert vector.impact_weight == 1.0
    assert vector.is_critical() is True


def test_to_vector_local_event():
    event = InterpretedEvent("STATE_INIT", {})
    vector = to_vector(event)
    assert vector.impact_weight == 0.2


def test_to_vector_urgency_normalized():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    vector = to_vector(event)
    assert abs(vector.urgency_weight - 1.0) < 1e-9


def test_from_vector_roundtrip():
    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    vector = to_vector(event)
    back = from_vector(vector)
    assert back["impact"] == "critical"
    assert back["urgency"] == event.meaning["urgency"]


def test_bridge_all_37_events():
    taxonomy = get_taxonomy()
    events = taxonomy["events"]
    all_event_types = [
        event_type
        for cat_events in events.values()
        for event_type in cat_events
    ]
    assert len(all_event_types) >= 37

    for event_type in all_event_types:
        event = InterpretedEvent(event_type, {})
        vector = to_vector(event)
        assert 0.0 <= vector.impact_weight <= 1.0
        assert 0.0 <= vector.urgency_weight <= 1.0
