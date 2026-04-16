import os
import sys
import json
import time
import base64
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

OUTBOX_DIR_DEFAULT = r"outbox"
PRIVATE_KEY_PATH_DEFAULT = r"secrets\ed25519\ed25519_private.key"

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read().strip()

def load_private_key(priv_path):
    raw = read_bytes(priv_path)

    # accept raw 32 bytes, or hex-encoded 32 bytes (64 hex chars)
    if len(raw) == 64:
        try:
            raw = bytes.fromhex(raw.decode("ascii"))
        except Exception:
            pass

    if len(raw) != 32:
        raise ValueError("private key must be 32 bytes (got %d) at %s" % (len(raw), priv_path))

    return Ed25519PrivateKey.from_private_bytes(raw)

def canonicalize_payload(payload_obj):
    s = json.dumps(payload_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    # Usage:
    #   python tools/gen_signed_outbox_one.py
    #   python tools/gen_signed_outbox_one.py <outbox_dir> <private_key_path>
    outbox_dir = OUTBOX_DIR_DEFAULT
    priv_path = PRIVATE_KEY_PATH_DEFAULT

    if len(sys.argv) >= 2:
        outbox_dir = sys.argv[1]
    if len(sys.argv) >= 3:
        priv_path = sys.argv[2]

    os.makedirs(outbox_dir, exist_ok=True)

    if not os.path.exists(priv_path):
        print("PRIVATE KEY NOT FOUND:", priv_path, file=sys.stderr)
        return 2

    priv = load_private_key(priv_path)

    payload = {
        "schema": "mocka.outbox.v1",
        "kind": "signed_test",
        "created_at": utc_now_iso(),
        "nonce": int(time.time() * 1000),
        "note": "phase13-a signed outbox test"
    }

    msg = canonicalize_payload(payload)
    sig = priv.sign(msg)
    sig_b64 = base64.b64encode(sig).decode("ascii")

    obj = {
        "payload": payload,
        "signature": sig_b64
    }

    name = "%d_signed_test.json" % payload["nonce"]
    path = os.path.join(outbox_dir, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print("WROTE:", path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())