import csv
import json
import binascii
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

TRANSITION_LOG = "transition_log.csv"
CHAIN_LOG = "chain_signature_log.csv"
KEY_REGISTRY = "key_registry.json"

def load_registry():
    with open(KEY_REGISTRY, "r", encoding="utf-8") as f:
        return json.load(f)

def load_pub_from_registry(reg, key_id):
    return Ed25519PublicKey.from_public_bytes(
        binascii.a2b_base64(reg[key_id]["public_key"])
    )

def load_pub_from_base64(b64):
    return Ed25519PublicKey.from_public_bytes(
        binascii.a2b_base64(b64)
    )

def load_chain_signatures_set():
    with open(CHAIN_LOG, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return set(r["chain_signature"] for r in rows if r.get("chain_signature"))

def main():
    reg = load_registry()
    chain_sigs = load_chain_signatures_set()

    with open(TRANSITION_LOG, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prev = row["prev_chain_signature"]
            if prev not in chain_sigs:
                raise Exception("Transition prev_chain_signature not found in chain history")

            payload = (prev + row["new_public_key"]).encode("utf-8")

            old_pub = load_pub_from_registry(reg, row["old_key_id"])
            new_pub = load_pub_from_base64(row["new_public_key"])

            try:
                old_pub.verify(bytes.fromhex(row["old_key_signature"]), payload)
                new_pub.verify(bytes.fromhex(row["new_key_signature"]), payload)
            except InvalidSignature:
                raise Exception("Transition signature invalid")

    print("TRANSITION_VERIFY_OK")

if __name__ == "__main__":
    main()
