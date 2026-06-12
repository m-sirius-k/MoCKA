# test_phase_d.py
import json
from pathlib import Path

import pytest

from ..state_machine import ISEState, TRANSITIONS, can_transition, transition
from ..version_policy import VERSION_POLICY, get_policy
from ..lifecycle_manager import LifecycleStage, classify_snapshot, is_purge_eligible
from ..snapshot_manager import SNAPSHOT_MAX_GENERATIONS

_TAXONOMY_PATH = Path(__file__).resolve().parents[5] / "docs" / "mocka3" / "taxonomy.json"


# ── State Machine ──────────────────────────────────────────────

def test_valid_transition_initializing_to_active():
    assert can_transition(ISEState.INITIALIZING, ISEState.ACTIVE) is True
    assert transition(ISEState.INITIALIZING, ISEState.ACTIVE) == ISEState.ACTIVE


def test_invalid_transition_sealed():
    assert can_transition(ISEState.SEALED, ISEState.ACTIVE) is False
    with pytest.raises(ValueError):
        transition(ISEState.SEALED, ISEState.ACTIVE)


def test_all_valid_transitions():
    for current, nexts in TRANSITIONS.items():
        for nxt in nexts:
            assert can_transition(current, nxt) is True
            assert transition(current, nxt) == nxt


def test_all_invalid_transitions():
    for current in ISEState:
        allowed = set(TRANSITIONS.get(current, []))
        for nxt in ISEState:
            if nxt not in allowed:
                assert can_transition(current, nxt) is False
                with pytest.raises(ValueError):
                    transition(current, nxt)


# ── Event Taxonomy ─────────────────────────────────────────────

def test_taxonomy_json_exists():
    assert _TAXONOMY_PATH.exists()


def test_taxonomy_has_required_categories():
    with open(_TAXONOMY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    categories = data["categories"]
    for cat in ("state_transition", "state_operation", "audit", "lifecycle", "incident"):
        assert cat in categories
        assert "description" in categories[cat]
        assert "examples" in categories[cat]
        assert "severity_range" in categories[cat]


def test_taxonomy_version():
    with open(_TAXONOMY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == "1.1"


# ── Version Policy ─────────────────────────────────────────────

def test_snapshot_version_increments():
    policy = get_policy()
    assert policy["snapshot_retention"] == SNAPSHOT_MAX_GENERATIONS
    assert policy["snapshot_interval_revisions"] == 100
    assert policy["snapshot_interval_hours"] == 24


def test_version_format():
    policy = get_policy()
    assert isinstance(policy["major_version_triggers"], list)
    assert isinstance(policy["minor_version_triggers"], list)
    assert "state_machine_change" in policy["major_version_triggers"]
    assert "provider_added" in policy["minor_version_triggers"]
    assert policy is VERSION_POLICY


# ── データライフサイクル ─────────────────────────────────────────

def test_lifecycle_stages_defined():
    names = {s.value for s in LifecycleStage}
    assert names == {"raw", "active", "snapshot", "archived", "purged"}


def test_snapshot_retention_policy():
    # 最新世代はSNAPSHOT扱い
    assert classify_snapshot(0, ISEState.ACTIVE) == LifecycleStage.SNAPSHOT
    assert classify_snapshot(SNAPSHOT_MAX_GENERATIONS - 1, ISEState.ACTIVE) == LifecycleStage.SNAPSHOT

    # SNAPSHOT_MAX_GENERATIONS*2 を超えた世代はPURGED
    over = SNAPSHOT_MAX_GENERATIONS * 2
    assert classify_snapshot(over, ISEState.ACTIVE) == LifecycleStage.PURGED
    assert is_purge_eligible(over, ISEState.ACTIVE) is True

    # SEALED状態であればARCHIVED
    assert classify_snapshot(0, ISEState.SEALED) == LifecycleStage.ARCHIVED
    assert is_purge_eligible(0, ISEState.SEALED) is False
