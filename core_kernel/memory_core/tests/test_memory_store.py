"""
memory_core.tests.test_memory_store

MemoryStore(最小永続化層)に関するテスト。
"""

import json

from core_kernel.memory_core import MEMORY_RECORD_SCHEMA_VERSION, MemoryStore


def test_in_memory_fallback_save_and_load():
    store = MemoryStore()

    record = store.save("observation", {"finding": "test"})

    assert record["type"] == "observation"
    assert record["version"] == MEMORY_RECORD_SCHEMA_VERSION
    assert record["payload"] == {"finding": "test"}

    loaded = store.load(record["id"])
    assert loaded == record


def test_load_missing_id_returns_none():
    store = MemoryStore()
    assert store.load("does-not-exist") is None


def test_json_persistence_round_trip(tmp_path):
    path = tmp_path / "memory.json"
    store1 = MemoryStore(path=path)
    record = store1.save("context", {"context_id": "ctx-1"})

    assert path.exists()

    store2 = MemoryStore(path=path)
    loaded = store2.load(record["id"])

    assert loaded == record


def test_json_file_structure(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path=path)
    record = store.save("analysis_result", {"a": 1})

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert "records" in data
    assert record["id"] in data["records"]
    stored = data["records"][record["id"]]
    assert set(stored.keys()) == {"id", "type", "timestamp", "version", "session_id", "payload"}


def test_corrupted_file_falls_back_to_empty_store(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text("{ this is not valid json", encoding="utf-8")

    store = MemoryStore(path=path)

    assert store.query() == []

    record = store.save("observation", {"finding": "ok"})
    assert store.load(record["id"]) == record


def test_non_dict_json_falls_back_to_empty_store(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")

    store = MemoryStore(path=path)
    assert store.query() == []


def test_query_with_predicate():
    store = MemoryStore()
    store.save("observation", {"risk_level": "low"})
    store.save("observation", {"risk_level": "high"})
    store.save("context", {"foo": "bar"})

    high_risk = store.query(lambda r: r["type"] == "observation" and r["payload"]["risk_level"] == "high")

    assert len(high_risk) == 1
    assert high_risk[0]["payload"]["risk_level"] == "high"


def test_query_without_predicate_returns_all():
    store = MemoryStore()
    store.save("observation", {"a": 1})
    store.save("context", {"b": 2})

    all_records = store.query()
    assert len(all_records) == 2


def test_list_by_session_id():
    store = MemoryStore()
    store.save("context", {"v": 1}, session_id="session-a")
    store.save("context", {"v": 2}, session_id="session-a")
    store.save("context", {"v": 3}, session_id="session-b")

    session_a_records = store.list("session-a")

    assert len(session_a_records) == 2
    assert all(r["session_id"] == "session-a" for r in session_a_records)


def test_save_with_explicit_record_id_allows_overwrite(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path=path)

    store.save("observation", {"v": 1}, record_id="fixed-id")
    record2 = store.save("observation", {"v": 2}, record_id="fixed-id")

    assert record2["id"] == "fixed-id"
    assert store.load("fixed-id")["payload"] == {"v": 2}
    assert len(store.query()) == 1
