from pathlib import Path
import json
from base64 import b64decode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from canonical import canonical_bytes, canonical_loads, read_bytes
from key_registry_verify_v4 import load_registry, RegistryError

class SignatureError(Exception):
    pass

def pubkey_from_b64(b64: str) -> Ed25519PublicKey:
    raw = b64decode(b64)
    return Ed25519PublicKey.from_public_bytes(raw)

def verify_event_signatures(event_path: str | Path) -> None:
    active_keys, revoked_keys = load_registry()

    event = canonical_loads(read_bytes(event_path))

    threshold = event.get("threshold")
    sigs = event.get("signatures")

    if not isinstance(threshold, int) or threshold <= 0:
        raise SignatureError("Invalid threshold")

    if not isinstance(sigs, list) or len(sigs) == 0:
        raise SignatureError("Missing signatures")

    if len(sigs) < threshold:
        raise SignatureError(f"Insufficient signatures: {len(sigs)} < {threshold}")

    # 署名対象は署名フィールドなしのイベント本体
    unsigned = dict(event)
    unsigned.pop("signatures", None)
    msg = canonical_bytes(unsigned)

    seen_signers = set()
    ok_count = 0

    for s in sigs:
        key_id = s.get("key_id")
        sig_b64 = s.get("signature_b64")

        if not key_id or not sig_b64:
            raise SignatureError("Signature entry missing key_id or signature_b64")

        if key_id in seen_signers:
            raise SignatureError(f"Duplicate signer: {key_id}")
        seen_signers.add(key_id)

        if key_id in revoked_keys:
            raise SignatureError(f"Revoked key used: {key_id}")

        if key_id not in active_keys:
            raise SignatureError(f"Unknown or inactive key: {key_id}")

        pub_b64 = active_keys[key_id]["public_key_b64"]
        pub = pubkey_from_b64(pub_b64)

        try:
            pub.verify(b64decode(sig_b64), msg)
            ok_count += 1
        except InvalidSignature:
            raise SignatureError(f"Invalid signature for key_id: {key_id}")

    if ok_count < threshold:
        raise SignatureError(f"Threshold not met: ok={ok_count} threshold={threshold}")

    print(f"OK: signature verify PASS ({ok_count}/{threshold})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python event_signature_verify_v4.py <event_json>")
    verify_event_signatures(sys.argv[1])