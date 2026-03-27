import json
import hashlib
import datetime
import csv
from pathlib import Path
from cryptography.hazmat.primitives import serialization

LEDGER_PATH = Path("runtime/main/ledger.json")
PRIVATE_KEY_PATH = Path(r"J:\MoCKA_Observer_Node\observer_pack_latest\observer_private.pem")
SIGN_LOG = Path(r"J:\MoCKA_Observer_Node\observer_pack_latest\chain_signature_log.csv")

def calculate_head_hash():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    last_event = ledger[-1]
    raw = json.dumps(last_event, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def sign_hash(private_key, head_hash):
    # Ed25519はそのままsignする（padding不要）
    return private_key.sign(head_hash.encode()).hex()

def append_log(head_hash, signature):
    now = datetime.datetime.utcnow().isoformat()
    SIGN_LOG.parent.mkdir(parents=True, exist_ok=True)

    file_exists = SIGN_LOG.exists()

    with open(SIGN_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp","head_hash","signature"])
        writer.writerow([now, head_hash, signature])

def main():
    print("=== MoCKA Observer Seal Start ===")

    head_hash = calculate_head_hash()
    print("HEAD HASH:", head_hash)

    private_key = load_private_key()
    signature = sign_hash(private_key, head_hash)

    append_log(head_hash, signature)

    print("SIGNATURE CREATED")
    print("=== COMPLETE ===")

if __name__ == "__main__":
    main()
