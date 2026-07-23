"""WP-Schema-03 検証用サンプルレコード(テスト専用、実データではない)"""

EXAMPLE_RESTORE_PACKET_V1 = {
    "schema_version": "1.0",
    "packet_id": "RP_20260723_001",
    "governance_anchor_hash": "37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5",
    "runtime_evidence_ref": "RER_20260723_001",
    "decision_refs": ["GTR_20260723_001"],
    "event_range": {
        "from_event_id": "E20260723_000000000001",
        "to_event_id": "E20260723_467738871d146",
        "event_count": 17659,
    },
    "generated_at": "2026-07-23T08:00:00Z",
    "content_hash": "1" * 64,
    "immutable": True,
    "supersedes": None,
    "sequence": 1,
    "payload": {
        "immutable": {
            "philosophy": ["AIを信じるな、システムで縛れ"],
            "forbidden": [],
            "values": [],
        },
        "restore_5points": {},
        "session_context": "write_path_v1 bootstrap fixture",
    },
}

# supersede chain確認用: EXAMPLE_RESTORE_PACKET_V1 を継承した第2世代
EXAMPLE_RESTORE_PACKET_V1_SUPERSEDING = {
    **EXAMPLE_RESTORE_PACKET_V1,
    "packet_id": "RP_20260723_002",
    "supersedes": "RP_20260723_001",
    "sequence": 2,
}

# Freshness Contract不一致確認用(governance_anchor_hashが異なる = STALE_CONTEXT)
EXAMPLE_RESTORE_PACKET_V1_STALE = {
    **EXAMPLE_RESTORE_PACKET_V1,
    "packet_id": "RP_20260722_stale",
    "governance_anchor_hash": "0" * 64,
}
