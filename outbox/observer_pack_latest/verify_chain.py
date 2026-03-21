import csv
import json
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import binascii

CHAIN_LOG = "chain_signature_log.csv"
KEY_REGISTRY = "key_registry.json"

def load_registry():
    with open(KEY_REGISTRY, "r", encoding="utf-8") as f:
        return json.load(f)

def load_public_key(registry, key_id):
    pk_bytes = binascii.a2b_base64(registry[key_id]["public_key"])
    return Ed25519PublicKey.from_public_bytes(pk_bytes)

def verify_time(registry, key_id, signed_at):
    rec = registry[key_id]
    valid_from = datetime.fromisoformat(rec["valid_from"].replace("Z","+00:00"))
    valid_to = None
    if rec["valid_to"]:
        valid_to = datetime.fromisoformat(rec["valid_to"].replace("Z","+00:00"))
    t = datetime.fromisoformat(signed_at.replace("Z","+00:00"))
    if t < valid_from:
        raise Exception("Signature before key valid_from")
    if valid_to and t > valid_to:
        raise Exception("Signature after key valid_to")

def main():
    registry = load_registry()
    prev_signature = ""

    with open(CHAIN_LOG, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key_id = row["key_id"]
            signed_at = row["signed_at_utc"]
            index_sha256 = row["index_sha256"]
            prev_chain_signature = row["prev_chain_signature"]
            chain_signature = bytes.fromhex(row["chain_signature"])

            if prev_chain_signature != prev_signature:
                raise Exception("Chain break detected")

            verify_time(registry, key_id, signed_at)

            payload = (index_sha256 + prev_chain_signature).encode("utf-8")
            pub = load_public_key(registry, key_id)

            try:
                pub.verify(chain_signature, payload)
            except InvalidSignature:
                raise Exception("Signature verification failed")

            prev_signature = row["chain_signature"]

    print("CHAIN_VERIFY_OK")

if __name__ == "__main__":
    main()
