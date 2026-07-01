# tests/test_canary_overrides.py
# Canary Test: OVERRIDES enforcement -- event_gate rejection when Decision Evidence is absent
# TODO_401 v0.2 -- test_override_evidence_gap_is_rejected_by_event_gate
#
# Design reference: docs/governance/OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md
# Layer 2 (event_gate): Decision Evidence (before_state / after_state) must exist.
# When both are absent on an OVERRIDES-type operation, gate_validator.validate()
# returns REJECT-07, and process_event() returns status='rejected'.
# This test verifies that invariant is structurally enforced.

import sys
import json
import datetime
import pathlib
from pathlib import Path

# Make phi_os importable from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from flask import Flask
import phi_os.event_gate as eg
from phi_os.event_gate import gate_bp, process_event


# ── fixture: in-process call via process_event() (no HTTP, no real DB) ──────

@pytest.fixture
def patched_event_gate(tmp_path, monkeypatch):
    """
    Redirect DB_PATH to a temp SQLite DB with the correct schema.
    Uses process_event() directly (no HTTP overhead).
    Follows the pattern established in phi_os/tests/test_event_gate.py.
    """
    import sqlite3

    db_file = str(tmp_path / "canary_test_events.db")
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            when_ts TEXT,
            who_actor TEXT,
            what_type TEXT,
            where_component TEXT,
            where_path TEXT,
            why_purpose TEXT,
            how_trigger TEXT,
            channel_type TEXT,
            lifecycle_phase TEXT,
            risk_level TEXT,
            category_ab TEXT,
            target_class TEXT,
            title TEXT,
            short_summary TEXT,
            before_state TEXT,
            after_state TEXT,
            change_type TEXT,
            impact_scope TEXT,
            impact_result TEXT,
            related_event_id TEXT,
            trace_id TEXT,
            free_note TEXT,
            _imported_at TEXT,
            _source TEXT,
            ai_actor TEXT,
            session_id TEXT,
            severity TEXT,
            pattern_score REAL,
            recurrence_flag INTEGER,
            verified_by TEXT
        )
    """)
    conn.commit()
    conn.close()

    monkeypatch.setattr(eg, "DB_PATH", db_file)
    return db_file


# ── helpers ──────────────────────────────────────────────────────────────────

def _overrides_payload_with_evidence(**overrides):
    """Valid OVERRIDES operation payload WITH Decision Evidence (before_state present)."""
    base = {
        "who_actor":       "Claude-sonnet-4-6",
        "who_role":        "executor",
        "who_session":     "SESSION_20260701_090000",
        "what_type":       "config_change",
        "what_title":      "OVERRIDES: activate emergency override",
        "where_path":      "C:/Users/sirok/MoCKA/data/overrides_config.json",
        "where_component": "decision_policy.overrides",
        "why_purpose":     "OVERRIDES enforcement canary test - Decision Evidence present",
        "how_trigger":     "test_canary_overrides / TODO_401",
        "before_state":    "overrides_disabled",
        "after_state":     "overrides_active",
    }
    base.update(overrides)
    return base


def _overrides_payload_without_evidence(**overrides):
    """
    OVERRIDES operation payload WITHOUT Decision Evidence.
    Neither before_state nor after_state is provided.
    This represents the 'evidence gap' scenario that event_gate MUST reject (REJECT-07).
    """
    base = {
        "who_actor":       "Claude-sonnet-4-6",
        "who_role":        "executor",
        "who_session":     "SESSION_20260701_090000",
        "what_type":       "config_change",
        "what_title":      "OVERRIDES: activate emergency override",
        "where_path":      "C:/Users/sirok/MoCKA/data/overrides_config.json",
        "where_component": "decision_policy.overrides",
        "why_purpose":     "OVERRIDES enforcement canary test - NO Decision Evidence",
        "how_trigger":     "test_canary_overrides / TODO_401",
        # before_state and after_state intentionally omitted (evidence gap)
    }
    base.update(overrides)
    return base


# ── canary test ──────────────────────────────────────────────────────────────

def test_override_evidence_gap_is_rejected_by_event_gate(patched_event_gate):
    """
    Canary test (TODO_401 v0.2):
    OVERRIDES operation WITHOUT Decision Evidence MUST be rejected by event_gate.

    Design ref: OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md Layer 2:
      'event_gateがDecision Evidenceの存在を確認し、
       存在しない裁定結果をリジェクトする'
    Mechanism: gate_validator.validate() REJECT-07 triggers when
    both before_state and after_state are absent.
    """
    payload = _overrides_payload_without_evidence()
    result = process_event(payload)

    assert result["status"] == "rejected", (
        f"event_gate MUST reject OVERRIDES without Decision Evidence, "
        f"but returned: {result}"
    )
    errors = result.get("errors", [])
    assert any("REJECT-07" in e for e in errors), (
        f"REJECT-07 (before/after both absent) expected in errors, got: {errors}"
    )


def test_override_with_evidence_is_accepted(patched_event_gate):
    """
    Sanity check: OVERRIDES operation WITH Decision Evidence MUST pass event_gate.
    (Ensures the rejection above is specific to evidence gap, not general blockage.)
    """
    payload = _overrides_payload_with_evidence()
    result = process_event(payload)

    assert result["status"] == "ok", (
        f"event_gate MUST accept OVERRIDES with Decision Evidence, "
        f"but returned: {result}"
    )
    assert "event_id" in result


# ── last_run record update ────────────────────────────────────────────────────

def _update_canary_last_run(result: str = "PASS"):
    """
    Update data/tic/canary_overrides_last_run.json after test execution.
    Mirrors the 'Record last run timestamp' CI step from canary_overrides.yml.
    """
    record = {
        "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": result,
        "run_id": "local",
        "workflow": "test_canary_overrides.py (local run)",
    }
    repo_root = Path(__file__).resolve().parent.parent
    p = repo_root / "data" / "tic" / "canary_overrides_last_run.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# pytest hook: update last_run after the canary test completes
def pytest_sessionfinish(session, exitstatus):
    """
    After pytest session ends, record last run timestamp.
    Only updates when this specific test file is being run.
    """
    result_str = "PASS" if exitstatus == 0 else "FAIL"
    try:
        _update_canary_last_run(result_str)
    except Exception:
        pass
