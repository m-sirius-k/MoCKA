"""
MoCKA Core Kernel — event_contracts unit tests

Phase 3 成功条件の検証:
  - Event Contractが単独で利用可能
  - Version管理が機能する
  - Validationが機能する
  - Event Type Registryが利用できる
  - Replay Contractが定義されている
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from event_contracts import (
    EVENT_SCHEMA_VERSION,
    OPTIONAL_FIELDS,
    REPLAY_REQUIRED_FIELDS,
    REQUIRED_FIELDS,
    SUPPORTED_VERSIONS,
    EventType,
    EventTypeRegistry,
    build_event,
    is_replayable,
    is_supported_version,
    validate_event,
)


# ---------------------------------------------------------------------------
# Event Schema / build_event
# ---------------------------------------------------------------------------

def test_build_event_contains_required_fields():
    event = build_event(
        event_type=EventType.MODULE_REGISTERED,
        source_module="orchestra",
        payload={"module_id": "orchestra"},
    )

    for field_name in REQUIRED_FIELDS:
        assert field_name in event

    assert event["event_type"] == EventType.MODULE_REGISTERED
    assert event["event_version"] == EVENT_SCHEMA_VERSION
    assert event["source_module"] == "orchestra"
    assert event["payload"] == {"module_id": "orchestra"}
    # optional fields are absent unless specified
    for field_name in OPTIONAL_FIELDS:
        assert field_name not in event


def test_build_event_with_optional_fields():
    event = build_event(
        event_type=EventType.LIFECYCLE_CHANGED,
        source_module="memory",
        target_module="phi_os",
        payload={"state": "active"},
        metadata={"note": "test"},
    )

    assert event["target_module"] == "phi_os"
    assert event["metadata"] == {"note": "test"}


def test_build_event_generates_unique_ids():
    e1 = build_event("CHANGE_START", "orchestra", {})
    e2 = build_event("CHANGE_START", "orchestra", {})
    assert e1["event_id"] != e2["event_id"]


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------

def test_current_version_is_supported():
    assert is_supported_version(EVENT_SCHEMA_VERSION)
    assert EVENT_SCHEMA_VERSION in SUPPORTED_VERSIONS


def test_unknown_version_is_not_supported():
    assert not is_supported_version("999.0")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_validate_event_built_by_build_event_is_valid():
    event = build_event(EventType.MODULE_LOADED, "orchestra", {"ok": True})
    result = validate_event(event)
    assert result.valid is True
    assert result.errors == ()


def test_validate_event_missing_required_field():
    event = build_event(EventType.MODULE_LOADED, "orchestra", {"ok": True})
    del event["payload"]

    result = validate_event(event)

    assert result.valid is False
    assert any("payload" in e for e in result.errors)


def test_validate_event_unknown_field():
    event = build_event(EventType.MODULE_LOADED, "orchestra", {"ok": True})
    event["unexpected_field"] = "x"

    result = validate_event(event)

    assert result.valid is False
    assert any("unknown field" in e for e in result.errors)


def test_validate_event_bad_types():
    event = build_event(EventType.MODULE_LOADED, "orchestra", {"ok": True})
    event["payload"] = "not a dict"
    event["timestamp"] = "not-a-timestamp"

    result = validate_event(event)

    assert result.valid is False
    assert any("payload" in e for e in result.errors)
    assert any("timestamp" in e for e in result.errors)


def test_validate_event_unsupported_version():
    event = build_event(EventType.MODULE_LOADED, "orchestra", {"ok": True}, event_version="999.0")

    result = validate_event(event)

    assert result.valid is False
    assert any("event_version" in e for e in result.errors)


def test_validate_event_not_a_dict():
    result = validate_event("not-an-event")
    assert result.valid is False


def test_validate_event_with_type_registry():
    registry = EventTypeRegistry()
    event = build_event("UNKNOWN_TYPE", "orchestra", {"ok": True})

    result = validate_event(event, type_registry=registry)

    assert result.valid is False
    assert any("unregistered event_type" in e for e in result.errors)


def test_validate_event_with_type_registry_known_type():
    registry = EventTypeRegistry()
    event = build_event(EventType.CHANGE_START, "orchestra", {"ok": True})

    result = validate_event(event, type_registry=registry)

    assert result.valid is True


# ---------------------------------------------------------------------------
# Event Type Registry
# ---------------------------------------------------------------------------

def test_event_type_registry_preregisters_known_types():
    registry = EventTypeRegistry()
    for event_type in EventType.ALL:
        assert registry.is_registered(event_type)
    assert set(registry.list()) == set(EventType.ALL)


def test_event_type_registry_register_new_type():
    registry = EventTypeRegistry()
    registry.register("CUSTOM_EVENT", description="custom")

    assert registry.is_registered("CUSTOM_EVENT")
    assert registry.get("CUSTOM_EVENT")["description"] == "custom"


def test_event_type_registry_duplicate_register_raises():
    registry = EventTypeRegistry()
    with pytest.raises(ValueError):
        registry.register(EventType.CHANGE_START)


def test_event_type_registry_overwrite():
    registry = EventTypeRegistry()
    registry.register(EventType.CHANGE_START, description="updated", overwrite=True)
    assert registry.get(EventType.CHANGE_START)["description"] == "updated"


def test_event_type_registry_empty_when_not_preregistered():
    registry = EventTypeRegistry(preregister_known=False)
    assert registry.list() == ()


# ---------------------------------------------------------------------------
# Replay Contract
# ---------------------------------------------------------------------------

def test_replay_required_fields_subset_of_required_fields():
    assert set(REPLAY_REQUIRED_FIELDS).issubset(set(REQUIRED_FIELDS))


def test_is_replayable_true_for_valid_event_with_payload():
    event = build_event(EventType.CHANGE_DONE, "orchestra", {"file": "x.py"})
    assert is_replayable(event) is True


def test_is_replayable_false_for_empty_payload():
    event = build_event(EventType.CHANGE_DONE, "orchestra", {})
    assert is_replayable(event) is False


def test_is_replayable_false_for_invalid_event():
    event = build_event(EventType.CHANGE_DONE, "orchestra", {"file": "x.py"})
    del event["event_id"]
    assert is_replayable(event) is False
