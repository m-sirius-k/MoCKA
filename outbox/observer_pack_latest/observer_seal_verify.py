import csv
import hashlib
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

AUDIT_LOG = "observer_audit.log"
SEAL_LOG = "observer_audit_chain.csv"
PUB_PATH = "observer_public.pem"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def load_pub():
    with open(PUB_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def main():
    strict_latest = "--strict-latest" in sys.argv

    pub = load_pub()
    with open(SEAL_LOG, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    prev = ""
    for i, r in enumerate(rows):
        if r["prev_chain_signature"] != prev:
            raise Exception(f"CHAIN_LINK_INVALID at row {i}")

        payload = (r["audit_sha256"] + prev).encode("utf-8")
        sig = bytes.fromhex(r["chain_signature"])

        try:
            pub.verify(sig, payload)
        except InvalidSignature:
            raise Exception(f"SEAL_INVALID at row {i}")

        prev = r["chain_signature"]

    if strict_latest:
        current = sha256_file(AUDIT_LOG)
        if rows and rows[-1]["audit_sha256"] != current:
            raise Exception("LATEST_AUDIT_HASH_MISMATCH")

    print("OBSERVER_SEAL_VERIFY_OK")

if __name__ == "__main__":
    main()
