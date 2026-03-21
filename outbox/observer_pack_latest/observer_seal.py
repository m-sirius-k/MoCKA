import hashlib
import csv
import os
from datetime import datetime, UTC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

AUDIT_LOG = "observer_audit.log"
SEAL_LOG = "observer_audit_chain.csv"
KEY_PATH = "observer_private.pem"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def ensure_key():
    if os.path.exists(KEY_PATH):
        return
    priv = Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(KEY_PATH, "wb") as f:
        f.write(pem)

def load_priv():
    with open(KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def last_sig():
    if not os.path.exists(SEAL_LOG):
        return ""
    with open(SEAL_LOG, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        return rows[-1]["chain_signature"] if rows else ""

def main():
    ensure_key()
    if not os.path.exists(AUDIT_LOG):
        raise SystemExit("AUDIT_LOG_NOT_FOUND")

    audit_hash = sha256_file(AUDIT_LOG)
    prev = last_sig()
    payload = (audit_hash + prev).encode("utf-8")

    priv = load_priv()
    sig = priv.sign(payload).hex()

    exists = os.path.exists(SEAL_LOG)
    with open(SEAL_LOG, "a", newline="", encoding="utf-8") as w:
        fields = ["sealed_at_utc","audit_sha256","prev_chain_signature","chain_signature"]
        writer = csv.DictWriter(w, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "sealed_at_utc": datetime.now(UTC).isoformat(),
            "audit_sha256": audit_hash,
            "prev_chain_signature": prev,
            "chain_signature": sig
        })

    print("OBSERVER_SEAL_OK")
    print("audit_sha256=" + audit_hash)
    print("chain_signature=" + sig)

if __name__ == "__main__":
    main()
