import json
import os
import sqlite3
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DB = os.path.join(ROOT, "audit", "ed25519", "audit.db")
PUBLIC_KEY_PATH = os.path.join(ROOT, "audit", "ed25519", "keys", "ed25519_public.key")

SIGNATURE_ENFORCE = True

def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return Ed25519PublicKey.from_public_bytes(f.read())

def verify_signature(event_json):
    if "signature" not in event_json:
        return False

    sig = bytes.fromhex(event_json["signature"])
    payload = json.dumps(event_json["payload"], sort_keys=True, separators=(",", ":")).encode("utf-8")

    pub = load_public_key()
    try:
        pub.verify(sig, payload)
        return True
    except Exception:
        return False

def accept_event(event_path):
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    if SIGNATURE_ENFORCE:
        if not verify_signature(event):
            raise Exception("SIGNATURE VERIFICATION FAILED")

    conn = sqlite3.connect(AUDIT_DB)
    cur = conn.cursor()

    cur.execute("INSERT INTO ledger (event_id, chain_hash) VALUES (?, ?)",
                (event["event_id"], event["chain_hash"]))

    conn.commit()
    conn.close()

    print("ACCEPTED:", event["event_id"])

if __name__ == "__main__":
    import sys
    accept_event(sys.argv[1])