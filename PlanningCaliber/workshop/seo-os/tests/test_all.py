import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SEO_OS_TEST"] = "1"
import kernel.job_engine as je
je.DB_PATH = ":memory:"

import sqlite3
from data.init_db import init

@pytest.fixture(autouse=True)
def setup():
    je._memory_conn = None
    conn = je._con()
    conn.executescript(open(
        os.path.join(os.path.dirname(__file__),"../data/init_db.py"),
        encoding="utf-8"
    ).read().split('"""')[1])
    yield

def test_create_job():
    jid = je.create_job("テストLP", "lp", target="wordpress")
    assert jid.startswith("J")
    assert len(jid) == 16

def test_get_jobs_pending():
    je.create_job("案件A", "blog")
    je.create_job("案件B", "lp")
    jobs = je.get_jobs("pending")
    assert len(jobs) >= 2

def test_approve_job():
    jid = je.create_job("承認テスト", "lp")
    je.approve_job(jid)
    job = je.get_job(jid)
    assert job["status"] == "approved"
    assert job["approved_at"] is not None

def test_reject_job():
    jid = je.create_job("却下テスト", "blog")
    je.reject_job(jid, reason="品質不足")
    job = je.get_job(jid)
    assert job["status"] == "rejected"
    assert job["note"] == "品質不足"

def test_mocka_event_safe():
    je._mocka("TEST_EVENT", "J_DUMMY", "テスト")
    assert True
