# NOTE: Phase13-B enforced signature guard (single source of truth)
# FILE: C:\Users\sirok\MoCKA\src\mocka_audit\signature_guard.py
#
# Rule:
# - Any signing / accept attempt MUST be rejected unless key is active (and not expired).

from .key_policy import assert_key_active


def guard_before_signature(key_id: str) -> None:
    assert_key_active(key_id)


def accept_signed_payload(payload: dict) -> None:
    key_id = str(payload.get("key_id", "")).strip()
    if not key_id:
        raise RuntimeError("REJECTED: missing key_id")
    assert_key_active(key_id)