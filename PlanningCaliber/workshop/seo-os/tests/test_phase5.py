import pytest, os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from caliber.performance_ledger import PerformanceLedger
from caliber.selection_strategy import select
from caliber.ai_recommender import AIRecommender

# ── Performance Ledger ────────────────────────────
def test_record_success_increments():
    pl = PerformanceLedger()
    pl.record_success("test_worker_p5", 200)
    m  = pl.get("test_worker_p5")
    assert m["success_count"] >= 1
    assert m["consecutive_failures"] == 0

def test_record_failure_increments():
    pl = PerformanceLedger()
    pl.record_failure("test_worker_p5_f")
    m  = pl.get("test_worker_p5_f")
    assert m["failure_count"] >= 1
    assert m["consecutive_failures"] >= 1

def test_success_rate_no_history():
    pl = PerformanceLedger()
    sr = pl.success_rate("no_history_worker")
    assert sr == 1.0  # 実績なし → 最大信頼

def test_is_degraded_after_failures():
    pl = PerformanceLedger()
    for _ in range(3):
        pl.record_failure("degraded_worker")
    assert pl.is_degraded("degraded_worker", threshold=3)

# ── Selection Strategy ────────────────────────────
def test_strategy_priority():
    from workers.sftp_worker import SFTPWorker
    from workers.wordpress_worker import WordPressWorker
    candidates = [SFTPWorker(), WordPressWorker()]
    result = select(candidates, "priority")
    assert result is not None

def test_strategy_highest_success():
    from workers.sftp_worker import SFTPWorker
    candidates = [SFTPWorker()]
    result = select(candidates, "highest_success")
    assert result is not None

def test_strategy_unknown_falls_back():
    from workers.sftp_worker import SFTPWorker
    candidates = [SFTPWorker()]
    result = select(candidates, "nonexistent_strategy")
    assert result is not None

# ── AI Recommender ────────────────────────────────
def test_recommender_returns_structure():
    rec = AIRecommender()
    result = rec.analyze()
    assert "warnings"     in result
    assert "suggestions"  in result
    assert "auto_actions" in result
    assert "summary"      in result

def test_recommender_detects_degraded():
    pl = PerformanceLedger()
    for _ in range(5):
        pl.record_failure("critical_worker_test")
    rec = AIRecommender()
    result = rec.analyze()
    names = [w["worker"] for w in result["warnings"]]
    assert "critical_worker_test" in names
