from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashlib import sha256
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
KEY_DIR = BASE / "keys"
REG_PATH = BASE / "KEY_REGISTRY_v4.jsonl"

AUTHORITIES = ["authority_a", "authority_b", "authority_c"]

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def write_bytes(p: Path, b: bytes) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)

def canonical_json_line(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def pubkey_raw_b64(pub) -> str:
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return b64encode(raw).decode("ascii")

def pubkey_fingerprint_sha256(pub) -> str:
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return sha256(raw).hexdigest()

def save_keypair(name: str):
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    write_bytes(KEY_DIR / f"{name}_private.pem", priv_pem)
    write_bytes(KEY_DIR / f"{name}_public.pem", pub_pem)

    entry = {
        "event_type": "register",
        "key_id": f"{name}_v1",
        "algorithm": "ed25519",
        "public_key_b64": pubkey_raw_b64(pub),
        "fingerprint_sha256": pubkey_fingerprint_sha256(pub),
        "status": "active",
        "activated_at": utc_now_iso()
    }
    return entry

def main():
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    for name in AUTHORITIES:
        entries.append(save_keypair(name))

    # overwrite registry deterministically for initial creation
    lines = [canonical_json_line(e) for e in entries]
    REG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("OK: keys generated in ./keys")
    print("OK: KEY_REGISTRY_v4.jsonl created")

if __name__ == "__main__":
    main()