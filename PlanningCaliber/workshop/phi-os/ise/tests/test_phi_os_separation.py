# test_phi_os_separation.py
"""STEP 1: PHI-OS core / registry 分離 検証"""
import inspect

import pytest

from phios.registry import taxonomy, rules
from phios import boot


def test_registry_taxonomy_readonly():
    data = taxonomy.get_taxonomy()
    assert data["status"] == "FROZEN"
    assert taxonomy.is_valid_event("SEAL") is True
    assert taxonomy.is_valid_event("UNKNOWN") is False
    assert taxonomy.get_category("STATE_CHANGE") == "state_operation"
    assert taxonomy.is_revision_update("STATE_CHANGE") is True
    assert taxonomy.is_revision_update("SEAL") is False


def test_core_cannot_write_taxonomy():
    src = inspect.getsource(taxonomy)
    for forbidden in ("def set_", "def write_", "def save_", "def update_taxonomy"):
        assert forbidden not in src


def test_registry_taxonomy_frozen():
    data = taxonomy.get_taxonomy()
    assert data["version"] == "1.1"
    assert len(data["categories"]) == 7


def test_boot_sequence_order():
    assert rules.BOOT_SEQUENCE == (
        "taxonomy_load",
        "rules_load",
        "event_pipeline_init",
        "adapter_registry_init",
        "mock_adapter_register",
        "execution_gate_check",
    )


def test_rules_forbidden_list():
    assert len(rules.FORBIDDEN_OPERATIONS) >= 6
    assert len(rules.ALLOWED_DECISION_CATEGORIES) == 3


def test_safe_boot_degraded_mode():
    assert boot.safe_boot(full=False) is True
