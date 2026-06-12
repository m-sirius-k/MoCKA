# test_phase_b.py
import pytest, json
from pathlib import Path
from ..capability_table import is_capability_valid, is_trust_sufficient
from ..ai_session_state import AISessionStore
from ..institution_contract import KnockRequest, check_contract
from ..diff_generator import generate_diff
from ..schema import InstitutionState, ProjectStatus


# ── Capability Table ──────────────────────────────────────────

def test_known_capability_valid():
    assert is_capability_valid("CAP_STATE_READ") is True

def test_unknown_capability_invalid():
    assert is_capability_valid("CAP_UNKNOWN") is False

def test_trust_sufficient():
    assert is_trust_sufficient("CAP_STATE_READ", "trial") is True

def test_trust_insufficient():
    assert is_trust_sufficient("CAP_LEDGER_WRITE", "trial") is False


# ── AI Session State ──────────────────────────────────────────

def test_ai_session_register(tmp_path):
    store = AISessionStore(tmp_path / "ai_session_state.json")
    entry = store.register_new("TestAI", role="executor")
    assert entry.ai_id == "TestAI"
    assert entry.trust_level == "trial"

def test_ai_session_update_knock(tmp_path):
    store = AISessionStore(tmp_path / "ai_session_state.json")
    store.register_new("TestAI", role="executor")
    store.update_knock("TestAI", applied_revision=10)
    assert store.get("TestAI").last_revision == 10


# ── Institution Contract ──────────────────────────────────────

def test_contract_allow(tmp_path):
    store = AISessionStore(tmp_path / "ai_session_state.json")
    store.register_new("GPT", role="architect", trust_level="institution_certified")
    req = KnockRequest(
        ai_id="GPT", capability=["CAP_STATE_READ"],
        role="architect", signature="", current_revision=0, timestamp=0
    )
    result = check_contract(req, store)
    assert result.allowed is True

def test_contract_unknown_capability(tmp_path):
    store = AISessionStore(tmp_path / "ai_session_state.json")
    store.register_new("GPT", role="architect", trust_level="trial")
    req = KnockRequest(
        ai_id="GPT", capability=["CAP_UNKNOWN"],
        role="architect", signature="", current_revision=0, timestamp=0
    )
    result = check_contract(req, store)
    assert result.allowed is False

def test_contract_trust_insufficient(tmp_path):
    store = AISessionStore(tmp_path / "ai_session_state.json")
    store.register_new("GPT", role="architect", trust_level="trial")
    req = KnockRequest(
        ai_id="GPT", capability=["CAP_LEDGER_WRITE"],
        role="architect", signature="", current_revision=0, timestamp=0
    )
    result = check_contract(req, store)
    assert result.allowed is False

def test_contract_auto_register_unknown_ai(tmp_path):
    """未登録AIはtrialで自動登録される"""
    store = AISessionStore(tmp_path / "ai_session_state.json")
    req = KnockRequest(
        ai_id="NewAI", capability=["CAP_STATE_READ"],
        role="observer", signature="", current_revision=0, timestamp=0
    )
    result = check_contract(req, store)
    assert result.allowed is True
    assert store.get("NewAI").trust_level == "trial"


# ── Diff Generator ────────────────────────────────────────────

def test_diff_add():
    old = {"a": 1}
    new = {"a": 1, "b": 2}
    patch = generate_diff(old, new)
    assert any(op["op"] == "add" and op["path"] == "/b" for op in patch)

def test_diff_replace():
    old = {"a": 1}
    new = {"a": 2}
    patch = generate_diff(old, new)
    assert patch == [{"op": "replace", "path": "/a", "value": 2}]

def test_diff_no_change():
    d = {"a": 1, "b": 2}
    assert generate_diff(d, d) == []
