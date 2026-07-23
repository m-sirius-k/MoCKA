"""WP-Schema-01 検証用サンプルレコード(テスト専用、実データではない)"""

EXAMPLE_RUNTIME_EVIDENCE_RECORD = {
    "record_id": "RER_20260723_001",
    "source_event_range": {
        "from_event_id": "E20260723_000000000001",
        "to_event_id": "E20260723_467738871d146",
        "event_count": 17659,
    },
    "hash": "0" * 64,
    "hash_method_spec": "sha256_json_sorted_v1",
    "generated_at": "2026-07-23T07:59:00Z",
    "generated_by": "governance.write_path.evidence (fixture)",
    "governance_anchor_hash": "37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5",
    "immutable": True,
}

INVALID_EXAMPLE_MISSING_HASH = {
    "record_id": "RER_20260723_002",
    "source_event_range": {
        "from_event_id": "E20260723_000000000001",
        "to_event_id": "E20260723_467738871d146",
        "event_count": 17659,
    },
    "hash_method_spec": "sha256_json_sorted_v1",
    "generated_at": "2026-07-23T07:59:00Z",
    "generated_by": "governance.write_path.evidence (fixture)",
    "immutable": True,
}
