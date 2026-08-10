from runtime.jarvis.record.ledger import JarvisLedger


def test_ledger_record_append():
    ledger = JarvisLedger()

    record = ledger.append(
        "JARVIS-TEST-001",
        "WAITING"
    )

    assert record["decision_id"] == "JARVIS-TEST-001"
    assert record["status"] == "WAITING"
    assert "timestamp" in record