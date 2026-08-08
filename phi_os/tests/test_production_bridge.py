from phi_os.runtime.production_bridge import ProductionBridge


def test_bridge_halt_production():
    bridge = ProductionBridge()

    incident = bridge.halt_production(
        evidence_reference="EV_TEST_001"
    )

    assert incident.state == "HALTED"
    assert incident.evidence_reference == "EV_TEST_001"


def test_bridge_can_resume_with_valid_decision():
    bridge = ProductionBridge()

    decision = {
        "gate_id": "HG-01",
        "approved": True,
    }

    assert bridge.can_resume(decision) is True


def test_bridge_rejects_invalid_decision():
    bridge = ProductionBridge()

    decision = {
        "gate_id": "INVALID",
        "approved": True,
    }

    assert bridge.can_resume(decision) is False
