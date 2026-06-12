# test_taxonomy_integration.py
"""ISE × Event Taxonomy v1.1 統合テスト"""
import subprocess
import sys
from pathlib import Path

import pytest

from .. import decision_ledger
from ..state_builder import emit_event
from ..taxonomy_validator import load_taxonomy

_ROOT = Path(__file__).resolve().parents[5]  # MoCKA/


# --- 統合① state_builder.emit_event -------------------------------------

def test_emit_known_event_type_ok():
    result = emit_event("STATE_INIT", actor="Claude")
    assert result["event_type"] == "STATE_INIT"
    assert result["category"] == "state_transition"
    assert result["actor"] == "Claude"


def test_emit_unknown_event_type_raises():
    with pytest.raises(ValueError):
        emit_event("NOT_A_REAL_EVENT")


def test_revision_increment_on_state_change():
    result = emit_event("STATE_DEGRADED")
    assert result["revision_increment"] is True


def test_no_revision_on_seal():
    result = emit_event("SEAL")
    assert result["revision_increment"] is False


# --- 統合② decision_ledger.append_decision -------------------------------

def test_decision_ledger_governance_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")
    entry = decision_ledger.append_decision(
        decision_type="AUTHORITY_REVOKE",
        actor="Human",
        before="delegated",
        after="revoked",
        reason="governance test",
    )
    assert entry["type"] == "AUTHORITY_REVOKE"


def test_decision_ledger_wrong_category_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")
    with pytest.raises(ValueError):
        decision_ledger.append_decision(
            decision_type="EVENT_WRITE",
            actor="Claude",
            before="none",
            after="written",
            reason="knowledge category, not allowed",
        )


# --- 統合③ verify_all taxonomy_integrity ---------------------------------

def test_verify_all_taxonomy_integrity_step():
    script = _ROOT / "governance" / "verify_taxonomy_integrity.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0
    assert "OK: taxonomy_integrity" in result.stdout


# --- 統合④ /api/ise/taxonomy ----------------------------------------------

def test_taxonomy_endpoint_200():
    import requests
    try:
        resp = requests.get("http://localhost:5000/api/ise/taxonomy", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("MoCKA server (localhost:5000) is not running")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["category_count"] == 7


def test_taxonomy_endpoint_frozen():
    import requests
    try:
        resp = requests.get("http://localhost:5000/api/ise/taxonomy", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("MoCKA server (localhost:5000) is not running")
    data = resp.json()
    assert data["status"] == "FROZEN"
    assert data["version"] == "1.1"


# --- taxonomy.json直接検証 --------------------------------------------------

def test_taxonomy_loaded_via_validator():
    data = load_taxonomy()
    assert data["status"] == "FROZEN"
    assert data["version"] == "1.1"
