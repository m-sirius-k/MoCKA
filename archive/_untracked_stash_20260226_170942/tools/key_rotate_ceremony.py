import os
import json
import hashlib
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = r"C:\Users\sirok\MoCKA"
REGISTRY_PATH = os.path.join(ROOT, "audit", "key_registry.json")
PRIVATE_DIR = os.path.join(ROOT, "audit", "private")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now_z() -> str:
    # timezone-aware UTC (no deprecation warning)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_registry() -> dict:
    # BOM tolerant read
    with open(REGISTRY_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_registry(data: dict) -> None:
    # Write BOM-less UTF-8 deterministically
    text = json.dumps(data, indent=2, ensure_ascii=False)
    with open(REGISTRY_PATH, "wb") as f:
        f.write(text.encode("utf-8"))


def generate_new_key_pems():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem.decode("utf-8"), public_pem.decode("utf-8")


def rotate_key() -> None:
    if not os.path.exists(REGISTRY_PATH):
        raise FileNotFoundError(f"registry missing: {REGISTRY_PATH}")

    os.makedirs(PRIVATE_DIR, exist_ok=True)

    registry = load_registry()
    old_chain = registry.get("rotation_chain_hash", "GENESIS")
    old_key_id = registry.get("active_key_id", "GENESIS")
    keys = registry.get("keys", [])

    now = utc_now_z()
    new_private_pem, new_public_pem = generate_new_key_pems()
    new_key_id = "key_" + now.replace(":", "").replace("-", "")

    # Old key -> inactive (verification only). GENESIS is conceptual, may not exist in list.
    for k in keys:
        if k.get("key_id") == old_key_id:
            k["status"] = "inactive"
            k["deactivated_at"] = now
            k["revocation_reason"] = "rotation"

    # Append new key
    keys.append(
        {
            "key_id": new_key_id,
            "public_key_pem": new_public_pem,
            "status": "active",
            "activated_at": now,
            "deactivated_at": None,
            "revocation_reason": None,
        }
    )

    registry["keys"] = keys
    registry["active_key_id"] = new_key_id

    chain_material = (old_chain + old_key_id + new_key_id + now).encode("utf-8")
    registry["rotation_chain_hash"] = sha256_hex(chain_material)

    save_registry(registry)

    # Private key is separated into audit/private/
    private_path = os.path.join(PRIVATE_DIR, f"{new_key_id}_private.pem")
    with open(private_path, "wb") as f:
        f.write(new_private_pem.encode("utf-8"))

    print("ROTATION_OK")
    print("NEW_KEY_ID:", new_key_id)
    print("CHAIN_HASH:", registry["rotation_chain_hash"])
    print("PRIVATE_KEY_PATH:", private_path)


if __name__ == "__main__":
    rotate_key()