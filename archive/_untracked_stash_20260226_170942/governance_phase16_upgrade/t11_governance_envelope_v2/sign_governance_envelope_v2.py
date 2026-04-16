# NOTE: sign_governance_envelope_v2.py (Phase16 T11.1 full)
# NOTE: Purpose: fill signature_ed25519 in an existing governance_envelope_v2_*.json
# NOTE: Inputs are outbox files produced by issue_governance_envelope_v2.py:
# NOTE:   *.json (envelope with empty signature)
# NOTE:   *.signed_bytes.txt (canonical bytes to sign; raw bytes)
# NOTE: Default key paths are used if env is missing.
# NOTE: Writes:
# NOTE:   *.sig (base64 signature text)
# NOTE:   updates *.json signature_ed25519 field
# NOTE: No unhandled exceptions.

import os
import sys
import json
import base64
from datetime import datetime, timezone

OUTBOX = r"C:\Users\sirok\MoCKA\outbox"

PUBKEY_ENV = "MOCKA_PHASE16_PUBKEY_PATH"
PRIVKEY_ENV = "MOCKA_PHASE16_PRIVKEY_PATH"

DEFAULT_PUBKEY = r"C:\Users\sirok\MoCKA\secrets\phase16\ed25519_public.pem"

# Try these in order if env is missing
DEFAULT_PRIVKEY_CANDIDATES = [
    r"C:\Users\sirok\MoCKA\secrets\phase16\ed25519_private.pem",
    r"C:\Users\sirok\MoCKA\secrets\phase16\ed25519_private_pkcs8.pem",
    r"C:\Users\sirok\MoCKA\secrets\phase16\private.pem",
]

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def write_text(path: str, s: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def pick_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return ""

def sign_ed25519(privkey_pem_path: str, msg: bytes) -> bytes:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    pem = read_bytes(privkey_pem_path)
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Private key is not Ed25519")
    return key.sign(msg)

def main():
    if len(sys.argv) != 2:
        print("Usage: python sign_governance_envelope_v2.py <event_id>")
        sys.exit(2)

    event_id = sys.argv[1].strip()
    prefix = f"governance_envelope_v2_{event_id}"

    env_json = os.path.join(OUTBOX, f"{prefix}.json")
    signed_bytes_path = os.path.join(OUTBOX, f"{prefix}.signed_bytes.txt")
    sig_out = os.path.join(OUTBOX, f"{prefix}.sig")

    if not os.path.exists(env_json):
        print("FAIL: envelope json missing:", env_json)
        sys.exit(1)
    if not os.path.exists(signed_bytes_path):
        print("FAIL: signed bytes missing:", signed_bytes_path)
        sys.exit(1)

    pubkey = os.environ.get(PUBKEY_ENV, "").strip() or DEFAULT_PUBKEY
    if not os.path.exists(pubkey):
        print("FAIL: public key missing:", pubkey)
        sys.exit(1)

    priv_env = os.environ.get(PRIVKEY_ENV, "").strip()
    privkey = priv_env if priv_env and os.path.exists(priv_env) else pick_existing(DEFAULT_PRIVKEY_CANDIDATES)
    if not privkey:
        print("FAIL: private key not found.")
        print("Set env and rerun:")
        print(f"  setx {PRIVKEY_ENV} C:\\Users\\sirok\\MoCKA\\secrets\\phase16\\ed25519_private.pem")
        sys.exit(1)

    env_obj = load_json(env_json)
    signed_bytes = read_bytes(signed_bytes_path)

    sig = sign_ed25519(privkey, signed_bytes)
    sig_b64 = base64.b64encode(sig).decode("ascii")

    env_obj["signature_ed25519"] = sig_b64
    notes = env_obj.get("notes", "")
    env_obj["notes"] = (notes + " " + f"signed_utc={utc_now()}").strip()

    save_json(env_json, env_obj)
    write_text(sig_out, sig_b64)

    print("OK: wrote signature file:", sig_out)
    print("OK: updated envelope json signature_ed25519:", env_json)
    print("OK: privkey used:", privkey)

if __name__ == "__main__":
    main()