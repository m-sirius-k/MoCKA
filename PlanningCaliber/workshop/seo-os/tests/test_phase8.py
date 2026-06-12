import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from caliber.bootstrap import initialize
from caliber.decision_ledger import DecisionLedger
from caliber.explain_engine import ExplainEngine
from kernel.simulation_engine import SimulationEngine
from mocka.mocka_bridge import MoCKABridge

initialize()

# ── Explain API (job_id) ───────────────────────────
def test_explain_job_unknown():
    result = ExplainEngine().explain_job("nonexistent_job")
    assert result["job_id"] == "nonexistent_job"
    assert result["worker_chosen"] is None
    assert result["alternatives_considered"] == []
    assert result["policy_checks"] == []
    assert "note" in result

def test_explain_job_found():
    from workers.sftp_worker import SFTPWorker
    dl = DecisionLedger()
    w  = SFTPWorker()
    dl.record(
        "upload_html","priority",w,[w],
        {"candidates":[{
            "name":w.name,
            "priority":w.priority,
            "success_rate":1.0,
            "avg_ms":0,
            "state":"ready"
        }], "score": 88},
        "JTEST_EXPLAIN8")

    result = ExplainEngine().explain_job("JTEST_EXPLAIN8")
    assert result["job_id"] == "JTEST_EXPLAIN8"
    assert result["worker_chosen"] == w.name
    assert len(result["alternatives_considered"]) >= 1
    assert result["score"] == 88

def test_explain_job_returns_required_keys():
    result = ExplainEngine().explain_job("JTEST_EXPLAIN8")
    for key in ("job_id","worker_chosen","reason",
                "alternatives_considered","policy_checks","score"):
        assert key in result

# ── Simulation Mode (dry run) ──────────────────────
def test_dry_run_basic_shape():
    result = SimulationEngine().dry_run("lp_pipeline", "")
    assert "would_run" in result
    assert "would_block" in result
    assert "estimated_score" in result
    assert isinstance(result["would_run"], list)
    assert isinstance(result["would_block"], list)

def test_dry_run_unknown_pipeline():
    result = SimulationEngine().dry_run("nonexistent_pipeline", "")
    assert result["pipeline_id"] == "nonexistent_pipeline"
    assert result["would_run"] == []

def test_dry_run_with_content_scores():
    html = "<html><head><meta name='viewport' content='width=device-width'>" \
           "<meta property='og:title' content='t'></head>" \
           "<body>" + "x" * 600 + "</body></html>"
    result = SimulationEngine().dry_run("lp_pipeline", html)
    assert result["estimated_score"] >= 0
    assert result["estimated_score"] <= 100

# ── MoCKA Bridge ────────────────────────────────────
class _FakeResponse:
    def __init__(self, ok=True, status_code=200, payload=None, text=""):
        self.ok = ok
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_forward_event_success(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        assert url.endswith("/api/phi-os-event")
        return _FakeResponse(ok=True, status_code=200, payload={"status": "ok"})

    monkeypatch.setattr("mocka.mocka_bridge.requests.post", fake_post)
    result = MoCKABridge().forward_event({"type": "TEST_EVENT"})
    assert result["ok"] is True
    assert result["status_code"] == 200

def test_forward_event_failure(monkeypatch):
    def fake_post(*a, **k):
        raise ConnectionError("refused")

    monkeypatch.setattr("mocka.mocka_bridge.requests.post", fake_post)
    result = MoCKABridge().forward_event({"type": "TEST_EVENT"})
    assert result["ok"] is False
    assert "error" in result

def test_get_context_success(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        assert url.endswith("/api/context/compose")
        return _FakeResponse(ok=True, status_code=200,
                              payload={"working_context": {"role": params["role"]}})

    monkeypatch.setattr("mocka.mocka_bridge.requests.get", fake_get)
    result = MoCKABridge().get_context(role="ai_claude")
    assert result["working_context"]["role"] == "ai_claude"

def test_get_context_failure(monkeypatch):
    def fake_get(*a, **k):
        raise ConnectionError("refused")

    monkeypatch.setattr("mocka.mocka_bridge.requests.get", fake_get)
    result = MoCKABridge().get_context()
    assert result["ok"] is False
    assert "error" in result

# ── Flask routes ────────────────────────────────────
@pytest.fixture
def client():
    from command_center.app import app
    return app.test_client()

def test_route_explain_job(client):
    res = client.get("/api/explain/JTEST_EXPLAIN8")
    assert res.status_code == 200
    data = res.get_json()
    assert data["job_id"] == "JTEST_EXPLAIN8"

def test_route_simulate_dry_run(client):
    res = client.post("/api/simulate", json={
        "pipeline_id": "lp_pipeline", "content_sample": ""
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "would_run" in data
    assert "would_block" in data
    assert "estimated_score" in data

def test_route_mocka_event(client, monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return _FakeResponse(ok=True, status_code=200, payload={"status": "ok"})
    monkeypatch.setattr("mocka.mocka_bridge.requests.post", fake_post)

    res = client.post("/api/mocka/event", json={"type": "TEST"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

def test_route_mocka_context(client, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return _FakeResponse(ok=True, status_code=200,
                              payload={"working_context": {"role": params["role"]}})
    monkeypatch.setattr("mocka.mocka_bridge.requests.get", fake_get)

    res = client.get("/api/mocka/context?role=ai_claude")
    assert res.status_code == 200
    assert res.get_json()["working_context"]["role"] == "ai_claude"
