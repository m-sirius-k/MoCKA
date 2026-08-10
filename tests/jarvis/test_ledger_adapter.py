from runtime.jarvis.record.adapter.ledger_adapter import LedgerAdapter


def test_ledger_adapter_record():
    adapter = LedgerAdapter()

    result = adapter.record(
        "TEST-004",
        "WAITING"
    )

    assert result["decision_id"] == "TEST-004"
    assert result["status"] == "WAITING"