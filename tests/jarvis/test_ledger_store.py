from runtime.jarvis.record.persistence.ledger_store import LedgerStore


def test_ledger_store_save_load(tmp_path):
    path = tmp_path / "ledger.jsonl"

    store = LedgerStore(path)

    record = {
        "decision_id": "TEST-007",
        "status": "WAITING"
    }

    store.save(record)

    result = store.load_all()

    assert result[0]["decision_id"] == "TEST-007"
    assert result[0]["status"] == "WAITING"