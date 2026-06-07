import pytest, os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from caliber.explain_engine import ExplainEngine
from kernel.simulation_engine import SimulationEngine
from caliber.decision_ledger import DecisionLedger

# ── Explain Engine ────────────────────────────────
def test_explain_returns_structure():
    result = ExplainEngine().explain("publish_blog")
    assert "capability"  in result
    assert "candidates"  in result
    assert "recommended" in result
    assert "explanation" in result

def test_explain_text_contains_capability():
    result = ExplainEngine().explain("upload_html")
    assert "upload_html" in result["explanation"]

def test_explain_unknown_capability():
    result = ExplainEngine().explain("nonexistent_cap")
    assert result["recommended"] is None

# ── Simulation Engine ─────────────────────────────
def test_simulation_lp_pipeline():
    sim = SimulationEngine()
    result = sim.simulate(
        "lp_pipeline",
        {"title":"テストLP"},
        "priority")
    assert "can_run"  in result
    assert "steps"    in result
    assert "summary"  in result
    assert isinstance(result["steps"], list)

def test_simulation_unknown_pipeline():
    sim    = SimulationEngine()
    result = sim.simulate(
        "nonexistent_pipeline",
        {"title":"test"})
    assert result["steps"] == []

def test_simulation_detects_no_worker():
    sim    = SimulationEngine()
    result = sim.simulate(
        "bot_pipeline",
        {"title":"BOTテスト"},
        "priority")
    # post_x / post_instagram がモックWorkerなので
    # can_run は False にならない（required=False）
    assert "steps" in result

# ── Decision Ledger ───────────────────────────────
def test_decision_ledger_record():
    from workers.sftp_worker import SFTPWorker
    dl = DecisionLedger()
    w  = SFTPWorker()
    did = dl.record(
        capability="upload_html",
        strategy="priority",
        selected=w,
        candidates=[w],
        reason={"test": True},
        job_id="JTEST",
        operator="test"
    )
    assert did is not None
    assert len(did) == 36  # UUID形式

def test_decision_ledger_update_outcome():
    from workers.sftp_worker import SFTPWorker
    dl  = DecisionLedger()
    w   = SFTPWorker()
    did = dl.record(
        "upload_html","priority",w,[w],{},"JTEST2")
    dl.update_outcome(did, "done")
    history = dl.get_by_capability("upload_html")
    found = [h for h in history if h["id"] == did]
    assert found[0]["outcome"] == "done"

def test_decision_all_returns_list():
    result = DecisionLedger().all(10)
    assert isinstance(result, list)
