"""
PHASE 3: caliber/ テストスイート
"""
import pytest

@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VASAI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("VASAI_HMAC_KEY", "test-key-123")
    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()
    yield


# ── BaseCALIBER / MedicalCALIBER ──────────────────────────
def test_medical_caliber_id():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    assert c.get_caliber_id() == "medical_v1"


def test_medical_classify():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    assert c.classify_event({"event_type": "treatment"}) == "decision"
    assert c.classify_event({"event_type": "incident"}) == "incident"
    assert c.classify_event({"event_type": "note"}) == "message"


def test_medical_approval_rules():
    from caliber.example_medical import MedicalCALIBER
    from core.models import RiskLevel
    c = MedicalCALIBER()
    rules = c.get_approval_rules()
    assert len(rules) >= 2
    auto_rules = [r for r in rules if r.auto_approve]
    assert any(r.risk_level == RiskLevel.NORMAL for r in auto_rules)


def test_medical_receive_from_intranet():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    data = {
        "patient_id": "P001",
        "event_type": "treatment",
        "description": "血圧測定",
        "physician": "山田先生",
        "department": "cardiology",
    }
    artifact = c.receive_from_intranet(data)
    assert artifact.source_app == "EMR"
    assert artifact.content["patient_id"] == "P001"
    assert "medical" in artifact.tags


def test_medical_format_for_intranet():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    artifact = c.receive_from_intranet({"patient_id": "P001", "event_type": "note"})
    from core import artifact_schema
    artifact.hash = artifact_schema.compute_hash(artifact)
    result = c.format_for_intranet(artifact)
    assert result["system"] == "EMR"
    assert "vasai_hash" in result


def test_medical_send_to_vasai():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    data = {"patient_id": "P002", "event_type": "note", "description": "定期検診"}
    artifact = c.receive_from_intranet(data)
    event_id = c.send_to_vasai(artifact)
    assert event_id.startswith("E")


def test_medical_full_flow():
    from caliber.example_medical import MedicalCALIBER
    c = MedicalCALIBER()
    result = c.process_intranet_request({
        "patient_id": "P003",
        "event_type": "note",
        "description": "問診",
    })
    assert result["system"] == "EMR"
    assert "vasai_hash" in result


# ── FinanceCALIBER ────────────────────────────────────────
def test_finance_caliber_id():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    assert c.get_caliber_id() == "finance_v1"


def test_finance_classify():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    assert c.classify_event({"transaction_type": "transfer"}) == "decision"
    assert c.classify_event({"transaction_type": "suspicious"}) == "incident"


def test_finance_large_tx_high_risk():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    data = {"transaction_type": "transfer", "amount": 50_000_000, "currency": "JPY"}
    artifact = c.receive_from_intranet(data)
    assert artifact.content["risk_level"] == "HIGH"


def test_finance_normal_tx():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    data = {"transaction_type": "transfer", "amount": 100_000}
    artifact = c.receive_from_intranet(data)
    assert artifact.content["risk_level"] == "NORMAL"


def test_finance_send_to_vasai():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    data = {"transaction_type": "transfer", "amount": 5000, "currency": "JPY"}
    artifact = c.receive_from_intranet(data)
    event_id = c.send_to_vasai(artifact)
    assert event_id.startswith("E")


def test_finance_format_for_intranet():
    from caliber.example_finance import FinanceCALIBER
    c = FinanceCALIBER()
    artifact = c.receive_from_intranet({"transaction_type": "transfer", "amount": 1000})
    from core import artifact_schema
    artifact.hash = artifact_schema.compute_hash(artifact)
    result = c.format_for_intranet(artifact)
    assert result["system"] == "CORE_BANKING"
    assert result["audit_trail"] is True


# ── Registry ──────────────────────────────────────────────
def test_caliber_registry():
    from caliber.base_caliber import register, get_registry
    from caliber.example_medical import MedicalCALIBER
    from caliber.example_finance import FinanceCALIBER
    register(MedicalCALIBER())
    register(FinanceCALIBER())
    reg = get_registry()
    assert "medical_v1" in reg
    assert "finance_v1" in reg
