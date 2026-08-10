from runtime.jarvis.record.ledger import JarvisLedger


def test_decision_ledger_flow():
    ledger = JarvisLedger()

    record = ledger.append(
        "DC-JARVIS-001",
        "APPROVED"
    )

    assert record["decision_id"] == "DC-JARVIS-001"
    assert record["status"] == "APPROVED"
    assert record["timestamp"] is not None