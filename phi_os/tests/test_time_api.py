# phi_os/tests/test_time_api.py
# Phase5 Step1 - Time API v0 単体テスト。
# 4エンドポイント(/time/state, /time/events, /time/replay, /time/audit)のHTTP200・正常応答を確認する。

import pytest
from flask import Flask

from phi_os.api.time_api import time_api_bp, _kernel


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(time_api_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_time_state(client):
    res = client.get("/time/state")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "state" in body


def test_time_events(client):
    _kernel.ingest({"type": "misc", "source": "test_time_api"})

    res = client.get("/time/events")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["count"] >= 1
    assert isinstance(body["events"], list)


def test_time_events_limit_offset(client):
    for i in range(5):
        _kernel.ingest({"type": "misc", "source": "test_time_api"})

    res = client.get("/time/events?limit=2&offset=1")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["events"]) == 2


def test_time_replay(client):
    _kernel.ingest({"type": "misc", "source": "test_time_api"})

    res = client.post("/time/replay", json={"mode": "current"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "state" in body


def test_time_audit(client):
    res = client.get("/time/audit")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "entries" in body
