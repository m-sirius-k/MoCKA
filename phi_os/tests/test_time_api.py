# phi_os/tests/test_time_api.py
# Phase5 Step1 - Time API v0 単体テスト。
# 4エンドポイント(/time/state, /time/events, /time/replay, /time/audit)のHTTP200・正常応答を確認する。
# Phase5 Step2 - Time Query Layer v0(/time/query)の5固定クエリ+未知クエリのテストを追加する。

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


def test_time_query_event_count(client):
    res = client.post("/time/query", json={"query": "event_count"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert isinstance(body["event_count"], int)


def test_time_query_last_snapshot(client):
    res = client.post("/time/query", json={"query": "last_snapshot"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "snapshot_id" in body
    assert "created_at" in body


def test_time_query_current_state(client):
    res = client.post("/time/query", json={"query": "current_state"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "state" in body


def test_time_query_replay_state(client):
    _kernel.ingest({"type": "misc", "source": "test_time_api"})

    res = client.post("/time/query", json={"query": "replay_state"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "state" in body


def test_time_query_audit_status(client):
    res = client.post("/time/query", json={"query": "audit_status"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "last_match" in body
    assert "drift_count" in body


def test_time_query_unknown(client):
    res = client.post("/time/query", json={"query": "not_a_real_query"})
    assert res.status_code == 400
    body = res.get_json()
    assert body["ok"] is False


def test_time_capabilities(client):
    res = client.get("/time/capabilities")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True

    names = {c["name"] for c in body["capabilities"]}
    assert names == {
        "event_count",
        "last_snapshot",
        "current_state",
        "replay_state",
        "audit_status",
    }
    for c in body["capabilities"]:
        assert "description" in c
        assert isinstance(c["description"], str)


@pytest.mark.parametrize("text,expected_keys", [
    ("イベント数を教えて", {"ok", "event_count"}),
    ("最後のsnapshotは？", {"ok", "snapshot_id", "created_at"}),
    ("現在状態を見せて", {"ok", "state"}),
    ("再生状態を確認", {"ok", "state"}),
    ("監査状態は？", {"ok", "last_match", "drift_count"}),
])
def test_time_semantic_query_resolves(client, text, expected_keys):
    res = client.post("/time/semantic_query", json={"query": text})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert expected_keys.issubset(body.keys())


def test_time_semantic_query_unresolved(client):
    res = client.post("/time/semantic_query", json={"query": "宇宙の意味は何ですか"})
    assert res.status_code == 400
    body = res.get_json()
    assert body["ok"] is False
    assert body["error"] == "UNRESOLVED_QUERY"
