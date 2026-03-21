# MoCKA Hash Specification v1.0

Algorithm:
SHA-256

Hash Input:
canonical_json(event without "hash")

Canonical Rules:
- UTF-8 encoding (no BOM)
- keys sorted lexicographically
- no whitespace
- separators = , :
- newline = \n

Chain Rule:
event.hash = sha256(event_string)
event.prev_hash = previous_event.hash

Genesis Rule:
prev_hash = "0"
