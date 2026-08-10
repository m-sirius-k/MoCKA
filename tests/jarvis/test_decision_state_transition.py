from runtime.jarvis.record.ledger import JarvisLedger


def test_decision_state_transition():
    ledger = JarvisLedger()

    waiting = ledger.append(
        "DC-JARVIS-STATE-001",
        "WAITING"
    )

    approved = ledger.append(
        "DC-JARVIS-STATE-001",
        "APPROVED"
    )

    assert waiting["status"] == "WAITING"
    assert approved["status"] == "APPROVED"
    assert waiting["decision_id"] == approved["decision_id"]