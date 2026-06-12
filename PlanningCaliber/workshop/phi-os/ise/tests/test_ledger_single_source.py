# test_ledger_single_source.py
"""STEP 4: EventLedger 単一ソース化 検証"""
import subprocess
import sys
from pathlib import Path

from .. import decision_ledger
from phios.ledger_gate import rebuild_state_from_ledger, verify_ledger_is_source_of_truth

_MOCKA_ROOT = Path(__file__).resolve().parents[5]


def test_state_rebuildable_from_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")

    decision_ledger.append_decision(
        decision_type="STATE_INIT", actor="Claude",
        before="initializing", after="active", reason="boot",
    )
    e1 = decision_ledger.append_decision(
        decision_type="STATE_DEGRADED", actor="ISE",
        before="active", after="degraded", reason="timeout",
        prev_hash=decision_ledger.read_ledger()[-1]["hash"],
    )
    decision_ledger.append_decision(
        decision_type="STATE_RECOVERED", actor="Human",
        before="degraded", after="active", reason="recovered",
        prev_hash=e1["hash"],
    )

    rebuilt = rebuild_state_from_ledger()
    # STATE_INIT(no), STATE_DEGRADED(yes), STATE_RECOVERED(yes) -> revision=2
    assert rebuilt["revision"] == 2
    assert rebuilt["entry_count"] == 3


def test_ledger_is_source_of_truth(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")
    decision_ledger.append_decision(
        decision_type="STATE_INIT", actor="Claude",
        before="initializing", after="active", reason="boot",
    )
    ok, msg = verify_ledger_is_source_of_truth()
    assert ok is True
    assert "1 entries OK" in msg


def test_no_direct_db_write():
    result = subprocess.run(
        ["grep", "-r", "sqlite3.connect", str(_MOCKA_ROOT / "PlanningCaliber" / "workshop" / "phi-os"),
         "--include=*.py"],
        capture_output=True, text=True,
    )
    lines = [
        l for l in result.stdout.splitlines()
        if "/tests/" not in l.replace("\\", "/")
        and "decision_ledger.py" not in l
        and "snapshot_manager.py" not in l
        and "state_provider.py" not in l
    ]
    assert lines == []


def test_cache_is_derived_only(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")
    decision_ledger.append_decision(
        decision_type="STATE_INIT", actor="Claude",
        before="initializing", after="active", reason="boot",
    )
    # current_state.json相当のcacheが存在しなくてもLedgerから再構築可能
    rebuilt_before = rebuild_state_from_ledger()
    rebuilt_after = rebuild_state_from_ledger()
    assert rebuilt_before == rebuilt_after
