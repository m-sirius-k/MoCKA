# test_phase_e.py
import json

from .. import decision_ledger
from .. import fluid_connector


# ── Decision Ledger ────────────────────────────────────────────

def test_decision_ledger_append(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")

    entry = decision_ledger.append_decision(
        decision_type="state_transition",
        actor="Claude",
        before="initializing",
        after="active",
        reason="phase_e_test",
    )

    assert entry["type"] == "state_transition"
    assert "hash" in entry

    entries = decision_ledger.read_ledger()
    assert len(entries) == 1
    assert entries[0]["after"] == "active"


def test_decision_ledger_verify_chain(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")

    e1 = decision_ledger.append_decision("state_transition", "Claude", "initializing", "active", "r1")
    decision_ledger.append_decision("knock_response", "GPT", "active", "active", "r2", prev_hash=e1["hash"])

    ok, msg = decision_ledger.verify_chain()
    assert ok is True
    assert "2 entries OK" in msg


def test_decision_ledger_tamper_detection(tmp_path, monkeypatch):
    ledger_path = tmp_path / "decision_ledger.jsonl"
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", ledger_path)

    decision_ledger.append_decision("state_transition", "Claude", "initializing", "active", "r1")

    # 改ざん: after を書き換えてhashを更新せずに保存
    entries = decision_ledger.read_ledger()
    entries[0]["after"] = "sealed"
    with open(ledger_path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    ok, msg = decision_ledger.verify_chain()
    assert ok is False
    assert "Hash mismatch" in msg


# ── Fluid Connector ────────────────────────────────────────────

def test_fluid_connector_known_transition():
    delta = fluid_connector.compute_delta("initializing", "active")
    assert delta == {"dx": 0.05, "dy": 0.10, "dz": 0.05}


def test_fluid_connector_unknown_transition_returns_zero():
    delta = fluid_connector.compute_delta("active", "initializing")
    assert delta == {"dx": 0.0, "dy": 0.0, "dz": 0.0}


# ── /api/ise/ledger エンドポイント相当 ───────────────────────────

def test_ledger_endpoint_200(tmp_path, monkeypatch):
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", tmp_path / "decision_ledger.jsonl")
    decision_ledger.append_decision("state_transition", "Claude", "initializing", "active", "r1")

    ok, msg = decision_ledger.verify_chain()
    entries = decision_ledger.read_ledger()
    response = {"ok": ok, "message": msg, "entries": entries}

    assert response["ok"] is True
    assert len(response["entries"]) == 1


# ── trajectory.csv 追記 ───────────────────────────────────────

def test_trajectory_append(tmp_path, monkeypatch):
    traj_path = tmp_path / "trajectory.csv"
    monkeypatch.setattr(fluid_connector, "TRAJECTORY_PATH", traj_path)

    ok = fluid_connector.notify_trajectory("initializing", "active", "E_TEST_001")
    assert ok is True
    assert traj_path.exists()

    content = traj_path.read_text(encoding="utf-8")
    assert "E_TEST_001" in content
    assert "initializing,active" in content
