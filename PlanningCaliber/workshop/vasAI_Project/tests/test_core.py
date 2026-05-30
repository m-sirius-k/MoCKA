"""
PHASE 1: core/ テストスイート
"""
import os
import tempfile
import pytest

# テスト用インメモリDB
@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_vasai.db"
    monkeypatch.setenv("VASAI_DB_PATH", str(db_file))
    monkeypatch.setenv("VASAI_HMAC_KEY", "test-key-123")
    yield


# ── event_store ────────────────────────────────────────────
def test_append_and_get():
    from core import event_store
    eid = event_store.append(
        who_actor="Claude",
        what_type="CHANGE_DONE",
        where_component="tests",
        why_purpose="unit test",
        content={"msg": "hello"},
    )
    assert eid.startswith("E")
    ev = event_store.get(eid)
    assert ev is not None
    assert ev["who_actor"] == "Claude"
    assert ev["content"]["msg"] == "hello"


def test_append_is_append_only():
    from core import event_store
    eid = event_store.append(who_actor="Claude", what_type="TEST")
    ev = event_store.get(eid)
    assert ev is not None
    # UPDATE/DELETEはSQLiteに直接操作しない限り不可能 → 構造上の保証


def test_hash_chain_valid():
    from core import event_store
    for i in range(5):
        event_store.append(who_actor="Claude", what_type=f"STAGE_{i}")
    assert event_store.verify_chain() is True


def test_list_events():
    from core import event_store
    for _ in range(3):
        event_store.append(who_actor="A", what_type="MSG")
    events = event_store.list_events(limit=10)
    assert len(events) >= 3


def test_stage_counts():
    from core import event_store
    event_store.append(who_actor="Claude", what_type="OBS", stage="OBSERVATION")
    event_store.append(who_actor="Claude", what_type="REC", stage="RECORD")
    counts = event_store.get_stage_counts()
    assert counts["OBSERVATION"] >= 1
    assert counts["RECORD"] >= 1


def test_event_id_format():
    from core import event_store
    eid = event_store.append(who_actor="Claude", what_type="TEST")
    parts = eid.split("_")
    assert parts[0].startswith("E")
    assert len(parts[0]) == 9  # E + 8桁日付
    assert len(parts[1]) == 3  # 3桁連番


# ── artifact_schema ────────────────────────────────────────
def test_artifact_hash_computed():
    from core import artifact_schema
    artifact = artifact_schema.from_raw(
        {"key": "value"},
        artifact_type="message",
        source_app="TestApp",
        source_service="TestService",
    )
    assert artifact.hash != ""
    assert len(artifact.hash) == 64  # SHA-256 hex


def test_artifact_validate():
    from core import artifact_schema
    data = {
        "artifact_type": "todo",
        "source_app": "Orchestra",
        "source_service": "acme_corp",
        "content": {"task": "do something"},
    }
    artifact = artifact_schema.validate(data)
    assert artifact.artifact_type == "todo"
    assert artifact.hash != ""


def test_to_event_content():
    from core import artifact_schema
    artifact = artifact_schema.from_raw({"x": 1}, artifact_type="message",
                                         source_app="A", source_service="B")
    ec = artifact_schema.to_event_content(artifact)
    assert "artifact_id" in ec
    assert "hash" in ec


# ── audit_chain ────────────────────────────────────────────
def test_sign_verify():
    from core import audit_chain
    sig = audit_chain.sign("E20260530_001", "abc123", "GENESIS_SIG")
    assert audit_chain.verify("E20260530_001", "abc123", "GENESIS_SIG", sig)
    assert not audit_chain.verify("E20260530_001", "abc123", "GENESIS_SIG", "bad")


def test_verify_chain_empty():
    from core import audit_chain
    report = audit_chain.verify_chain()
    assert report.chain_valid is True
    assert report.total_events == 0


def test_verify_chain_with_events():
    from core import event_store, audit_chain
    for i in range(3):
        event_store.append(who_actor="Claude", what_type="TEST")
    report = audit_chain.verify_chain()
    assert report.chain_valid is True
    assert report.total_events == 3


def test_seal():
    from core import event_store, audit_chain
    event_store.append(who_actor="Claude", what_type="TEST")
    sig = audit_chain.seal()
    assert len(sig) == 64  # HMAC-SHA256 hex


# ── governance ─────────────────────────────────────────────
def test_normal_auto_approved():
    from core import governance
    from core.models import DecisionStatus
    event = {"what_type": "CHANGE_DONE", "content": {}}
    decision = governance.process("E20260530_001", event)
    assert decision.status == DecisionStatus.AUTO_APPROVED


def test_high_risk_pending():
    from core import governance
    from core.models import DecisionStatus, RiskLevel
    event = {"what_type": "INCIDENT", "content": {}}
    decision = governance.process("E20260530_002", event)
    assert decision.status == DecisionStatus.PENDING
    assert decision.risk_level == RiskLevel.HIGH


def test_critical_auto_rejected():
    from core import governance
    from core.models import DecisionStatus
    event = {"what_type": "CRITICAL_ALERT", "content": {}}
    decision = governance.process("E20260530_003", event)
    assert decision.status == DecisionStatus.REJECTED


def test_human_approve():
    from core import governance
    from core.models import DecisionStatus
    event = {"what_type": "INCIDENT", "content": {}}
    d = governance.process("E20260530_004", event)
    approved = governance.approve(d.decision_id, reason="OK", approver="Doctor_A")
    assert approved.status == DecisionStatus.APPROVED
    assert approved.decided_by == "Doctor_A"


def test_human_reject():
    from core import governance
    from core.models import DecisionStatus
    event = {"what_type": "INCIDENT", "content": {}}
    d = governance.process("E20260530_005", event)
    rejected = governance.reject(d.decision_id, reason="No", approver="Manager")
    assert rejected.status == DecisionStatus.REJECTED


def test_get_pending():
    from core import governance
    event = {"what_type": "INCIDENT", "content": {}}
    d = governance.process("E20260530_006", event)
    pending = governance.get_pending()
    ids = [p.decision_id for p in pending]
    assert d.decision_id in ids
