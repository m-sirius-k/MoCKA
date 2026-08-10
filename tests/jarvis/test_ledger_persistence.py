from runtime.jarvis.record.ledger import JarvisLedger


def test_ledger_persistence_memory():
    ledger = JarvisLedger()

    ledger.append(
        "JARVIS-PERSIST-001",
        "APPROVED"
    )

    assert len(ledger.records) == 1
    assert ledger.records[0]["decision_id"] == "JARVIS-PERSIST-001"