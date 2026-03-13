import json
from pathlib import Path
from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
KEYS = BASE / "keys"

THRESHOLD = 2

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def load_priv(p: Path) -> Ed25519PrivateKey:
    return serialization.load_pem_private_key(read_bytes(p), password=None)

def main():
    SAMPLES.mkdir(parents=True, exist_ok=True)

    payload = {
        "message": "MoCKA v4 Responsibility Proof",
        "value": 42
    }

    event_core = {
        "created_at": utc_now_iso(),
        "payload": payload,
        "threshold": THRESHOLD
    }

    # event_id is derived from canonical core (stable within generation)
    event_id = sha256(canonical_bytes(event_core)).hexdigest()

    event = {
        "event_id": event_id,
        "created_at": event_core["created_at"],
        "payload": event_core["payload"],
        "threshold": event_core["threshold"]
    }

    msg = canonical_bytes(event)

    signers = [
        ("authority_a_v1", KEYS / "authority_a_private.pem"),
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
    ]

    sigs = []
    for key_id, priv_path in signers:
        priv = load_priv(priv_path)
        sig = priv.sign(msg)
        sigs.append({
            "key_id": key_id,
            "signature_b64": b64encode(sig).decode("ascii")
        })

    event["signatures"] = sigs

    out_path = SAMPLES / "valid_2_of_3.json"
    out_path.write_bytes(canonical_bytes(event) + b"\n")

    print("OK: samples/valid_2_of_3.json created")

if __name__ == "__main__":
    main()