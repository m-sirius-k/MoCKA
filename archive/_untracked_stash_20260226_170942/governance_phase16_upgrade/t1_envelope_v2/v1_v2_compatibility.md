# v1/v2 Compatibility
Generated: 2026-02-25T00:31:32.804381Z

v1: signs payload bytes only.
v2: signs canonical envelope (event_id, chain_hash, timestamp, payload_hash, key_id).

All new issuance MUST use v2.
