from __future__ import annotations

import json
import os
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


ROOT = Path(__file__).resolve().parents[1]
KEYS_DIR = ROOT / "keys"
PRIVATE_DIR = KEYS_DIR / "private"
PUBLIC_DIR = KEYS_DIR / "public"
REGISTRY_PATH = KEYS_DIR / "public_keys.json"


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main():
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()

    raw_pub = pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    key_id = sha256(raw_pub).hexdigest()

    private_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_path = PRIVATE_DIR / f"ed25519_{key_id}.pem"
    pub_path = PUBLIC_DIR / f"ed25519_{key_id}.pem"

    priv_path.write_bytes(private_pem)
    pub_path.write_bytes(public_pem)

    registry = {
        "schema": "mocka.keys.ed25519.registry.v1",
        "keys": {
            key_id: {
                "key_id": key_id,
                "public_pem_path": str(pub_path.relative_to(ROOT)).replace("\\", "/"),
                "created_at_utc": now_utc(),
                "status": "active",
            }
        },
    }

    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("OK")
    print("key_id =", key_id)
    print("private =", priv_path)
    print("public  =", pub_path)
    print("registry=", REGISTRY_PATH)


if __name__ == "__main__":
    main()