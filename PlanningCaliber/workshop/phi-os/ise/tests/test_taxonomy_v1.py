# test_taxonomy_v1.py
"""Event Taxonomy v1.1 検証テスト"""
import json
from pathlib import Path

from ..taxonomy_validator import VALID_CATEGORIES, is_valid_category, is_valid_event_type

_TAXONOMY_PATH = Path(__file__).resolve().parents[5] / "docs" / "mocka3" / "taxonomy.json"


def _load():
    with open(_TAXONOMY_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_state_transition_category_exists():
    data = _load()
    assert "state_transition" in data["categories"]
    assert "STATE_INIT" in data["events"]["state_transition"]


def test_state_operation_category_exists():
    data = _load()
    assert "state_operation" in data["categories"]
    assert "CHANGE_START" in data["events"]["state_operation"]
    assert "CHANGE_DONE" in data["events"]["state_operation"]


def test_state_change_removed():
    data = _load()
    assert "state_change" not in data["categories"]
    assert "state_change" not in data["events"]


def test_revoke_not_in_incident():
    data = _load()
    assert "REVOKE" not in data["events"]["incident"]


def test_authority_revoke_in_governance():
    data = _load()
    assert "AUTHORITY_REVOKE" in data["events"]["governance"]


def test_category_count_is_7():
    data = _load()
    assert len(data["categories"]) == 7
    assert set(data["categories"].keys()) == VALID_CATEGORIES


def test_validator_helpers():
    assert is_valid_category("governance") is True
    assert is_valid_category("state_change") is False
    assert is_valid_event_type("governance", "AUTHORITY_REVOKE") is True
    assert is_valid_event_type("incident", "REVOKE") is False
