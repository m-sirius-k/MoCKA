import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from caliber.bootstrap import initialize
from caliber.decision_replay import DecisionReplayer
from kernel.simulation_diff import SimulationDiff
from caliber.decision_policy import DecisionPolicyEngine

initialize()

# ── Bootstrap ──────────────────────────────────────
def test_bootstrap_idempotent():
    """2回呼んでも安全（冪等性）"""
    initialize()
    initialize()
    assert True

def test_bootstrap_registers_workers():
    from caliber.capability_registry import CapabilityRegistry
    caps = CapabilityRegistry.all_capabilities()
    assert "publish_blog" in caps
    assert "upload_html"  in caps

# ── Decision Replay ────────────────────────────────
def test_replay_unknown_id():
    result = DecisionReplayer().replay("nonexistent")
    assert "error" in result

def test_replay_returns_structure():
    from caliber.decision_ledger import DecisionLedger
    from workers.sftp_worker import SFTPWorker
    dl  = DecisionLedger()
    w   = SFTPWorker()
    did = dl.record(
        "upload_html","priority",w,[w],
        {"candidates":[{
            "name":w.name,
            "priority":w.priority,
            "success_rate":1.0,
            "avg_ms":0,
            "state":"ready"
        }]},
        "JTEST_REPLAY")
    result = DecisionReplayer().replay(did)
    assert result["decision_id"] == did
    assert result["capability"]  == "upload_html"
    assert len(result["candidates"]) >= 1

# ── Simulation Diff ────────────────────────────────
def test_diff_same_pipeline():
    result = SimulationDiff().diff(
        "lp_pipeline","lp_pipeline",
        {"title":"test","type":"lp","content":"x"*600})
    assert result["diff"]["changed"]  == []
    assert result["diff"]["added"]    == []
    assert result["diff"]["removed"]  == []

def test_diff_different_pipelines():
    result = SimulationDiff().diff(
        "lp_pipeline","blog_pipeline",
        {"title":"test","type":"blog","content":"x"*900})
    assert "diff"    in result
    assert "summary" in result["diff"]

# ── Decision Policy ────────────────────────────────
def test_add_policy():
    dp  = DecisionPolicyEngine()
    pid = dp.add_policy(
        "test_policy_p7",
        "min_success_rate","0.5")
    assert pid is not None
    policies = dp.get_policies()
    names = [p["name"] for p in policies]
    assert "test_policy_p7" in names

def test_disable_policy():
    dp  = DecisionPolicyEngine()
    pid = dp.add_policy(
        "test_disable_p7",
        "max_consecutive_failures","5")
    dp.disable(pid)
    policies = dp.get_policies()
    ids = [p["id"] for p in policies]
    assert pid not in ids

def test_policy_filters_candidate():
    from workers.sftp_worker import SFTPWorker
    from caliber.performance_ledger import PerformanceLedger
    dp  = DecisionPolicyEngine()
    pl  = PerformanceLedger()
    dp.add_policy(
        "test_filter_p7",
        "min_success_rate","0.99",
        capability="upload_html")
    workers = [SFTPWorker()]
    result  = dp.apply(workers,"upload_html",pl)
    assert isinstance(result, list)
