import json
import hashlib
from typing import Any, Dict, Tuple

def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _row_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    # 署名は row_sig 自体を除外して計算する（自己参照回避）
    if not isinstance(row, dict):
        return {}
    payload = dict(row)
    payload.pop("row_sig", None)
    return payload

def sign_row_soft(row: Dict[str, Any], secret: str) -> str:
    # soft署名（最小導入）: sha256( secret || canonical(row_without_row_sig) )
    if secret is None:
        secret = ""
    payload = _row_payload(row)
    b = secret.encode("utf-8") + b"|" + _canonical_json_bytes(payload)
    return hashlib.sha256(b).hexdigest()

def verify_row_soft(row: Dict[str, Any], sig: str, secret: str) -> Tuple[bool, str]:
    # returns (ok, expected_sig)
    expected = sign_row_soft(row, secret)
    return (expected == (sig or "")), expected
