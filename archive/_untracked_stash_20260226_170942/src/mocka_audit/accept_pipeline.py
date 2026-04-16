from typing import Dict, Any
from src.mocka_audit.signature_guard import guard_before_signature


def accept_signed_payload(signed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input contract (minimum):
      - signed["key_id"] is required
      - signed may include payload/signature etc (pipeline側で処理する前提)
    This function enforces revocation guard before any further processing.
    """
    if not isinstance(signed, dict):
        raise TypeError("signed must be a dict")

    key_id = str(signed.get("key_id", "")).strip()
    if not key_id:
        raise ValueError("signed.key_id is required")

    # 失効鍵はここで即停止
    guard_before_signature(key_id)

    return signed