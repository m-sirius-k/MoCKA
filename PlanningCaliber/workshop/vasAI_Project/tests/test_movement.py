"""
PHASE 2: movement/ テストスイート
"""
import os
import pytest

@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VASAI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("VASAI_HMAC_KEY", "test-key-123")
    # shadow_listenerをリセット
    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()
    yield


def make_movement():
    from movement.mocka_movement import MoCKAMovement
    return MoCKAMovement()


# ── MoCKAMovement ─────────────────────────────────────────
def test_observe_returns_artifact():
    m = make_movement()
    art = m.observe({"msg": "hello", "source_app": "TestApp", "source_service": "Acme"})
    assert art.artifact_id != ""
    assert art.source_app == "TestApp"


def test_record_returns_event_id():
    m = make_movement()
    art = m.observe({"msg": "hello", "source_app": "A", "source_service": "B"})
    eid = m.record(art)
    assert eid.startswith("E")


def test_detect_incident_normal():
    m = make_movement()
    art = m.observe({"msg": "ok", "source_app": "A", "source_service": "B"})
    eid = m.record(art)
    result = m.detect_incident(eid)
    assert result is False


def test_detect_incident_high():
    m = make_movement()
    art = m.observe({"artifact_type": "incident", "source_app": "A", "source_service": "B",
                     "risk_level": "HIGH"})
    eid = m.record(art)
    # INCIDENT判定はeventのwhat_typeかcontent.risk_levelに依存
    # 直接HIGH contentを持つイベントをappendしてテスト
    from core import event_store
    eid2 = event_store.append(
        who_actor="Test", what_type="INCIDENT",
        content={"risk_level": "HIGH"},
    )
    result = m.detect_incident(eid2)
    assert result is True


def test_check_recurrence():
    m = make_movement()
    count = m.check_recurrence("nonexistent_pattern")
    assert count == 0


def test_generate_prevention():
    m = make_movement()
    art = m.observe({"source_app": "A", "source_service": "B"})
    eid = m.record(art)
    candidates = m.generate_prevention(eid)
    assert len(candidates) == 3
    assert all("action" in c for c in candidates)


def test_decide_normal():
    m = make_movement()
    art = m.observe({"source_app": "A", "source_service": "B"})
    eid = m.record(art)
    from core.models import DecisionStatus
    decision = m.decide(eid)
    assert decision.status == DecisionStatus.AUTO_APPROVED


def test_act_approved():
    from core.models import Decision, RiskLevel, DecisionStatus
    m = make_movement()
    d = Decision(event_id="E001", risk_level=RiskLevel.NORMAL,
                 status=DecisionStatus.AUTO_APPROVED)
    result = m.act(d)
    assert result.success is True


def test_act_rejected():
    from core.models import Decision, RiskLevel, DecisionStatus
    m = make_movement()
    d = Decision(event_id="E001", risk_level=RiskLevel.CRITICAL,
                 status=DecisionStatus.REJECTED)
    result = m.act(d)
    assert result.success is False


def test_audit_report():
    m = make_movement()
    report = m.audit()
    assert report.chain_valid is True


def test_run_cycle_8_stages():
    m = make_movement()
    result = m.run_cycle({"source_app": "TestApp", "source_service": "Acme",
                          "msg": "complete cycle test"})
    assert result["stages_completed"] == 8
    assert result["chain_valid"] is True
    assert result["action_success"] is True


def test_run_cycle_incident():
    m = make_movement()
    # incident的な入力
    from core import event_store
    result = m.run_cycle({
        "source_app": "TestApp", "source_service": "Acme",
        "what_type": "INCIDENT", "risk_level": "HIGH",
    })
    assert result["stages_completed"] == 8


# ── ShadowMovement ────────────────────────────────────────
def make_shadow():
    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()
    from movement.shadow_movement import ShadowMovement
    return ShadowMovement()


def test_shadow_is_alive():
    s = make_shadow()
    assert s.is_alive() is True


def test_shadow_mirror():
    s = make_shadow()
    s.mirror({"stage": "OBSERVATION", "event_id": "E001"})
    stats = s.get_stats()
    assert stats["mirror_count"] == 1


def test_shadow_receives_mocka_events():
    s = make_shadow()  # この時点でlistener登録済み
    m = make_movement()
    art = m.observe({"source_app": "A", "source_service": "B"})
    m.record(art)
    stats = s.get_stats()
    assert stats["mirror_count"] >= 1


def test_shadow_verify_critical_ok():
    s = make_shadow()
    from core import event_store
    from core.models import Decision, RiskLevel
    eid = event_store.append(who_actor="Claude", what_type="INCIDENT",
                              content={"risk_level": "HIGH"})
    d = Decision(event_id=eid, risk_level=RiskLevel.HIGH)
    result = s.verify_critical(d)
    assert result is True


def test_shadow_verify_critical_missing_event():
    s = make_shadow()
    from core.models import Decision, RiskLevel
    d = Decision(event_id="NONEXISTENT", risk_level=RiskLevel.CRITICAL)
    result = s.verify_critical(d)
    assert result is False


def test_shadow_enter_degraded():
    s = make_shadow()
    status = s.enter_degraded_mode("test degraded")
    assert status.is_degraded is True
    assert status.available_pct == 0.75
    assert len(status.active_stages) == 5


def test_shadow_exit_degraded():
    s = make_shadow()
    s.enter_degraded_mode("test")
    s.exit_degraded_mode()
    status = s.get_status()
    assert status.is_degraded is False
    assert status.available_pct == 1.0


def test_shadow_sync_on_recovery():
    s = make_shadow()
    s.enter_degraded_mode("test")
    # 縮退中にmirrorイベント
    for i in range(3):
        s.mirror({"stage": "INCIDENT", "event_id": f"E00{i}"})
    count = s.sync_on_recovery()
    assert count == 3
    s.exit_degraded_mode()
    status = s.get_status()
    assert status.is_degraded is False


def test_shadow_full_status():
    s = make_shadow()
    status = s.get_status()
    assert status.available_pct == 1.0
    assert len(status.active_stages) == 8
