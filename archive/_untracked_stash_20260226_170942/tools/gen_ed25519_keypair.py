from __future__ import annotations

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption


ROOT = Path(__file__).resolve().parents[1]
KEY_DIR = ROOT / "audit" / "ed25519" / "keys"
VERIFY_PACK_DIR = ROOT / "audit" / "ed25519" / "verify_pack"

PRIV = KEY_DIR / "ed25519_private.key"
PUB = KEY_DIR / "ed25519_public.key"
PUB_VERIFY = VERIFY_PACK_DIR / "ed25519_public.key"


def main() -> int:
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    VERIFY_PACK_DIR.mkdir(parents=True, exist_ok=True)

    if PRIV.exists():
        raise SystemExit(f"PRIVATE_KEY_ALREADY_EXISTS: {PRIV}")

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    PRIV.write_bytes(priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()))
    PUB.write_bytes(pub.public_bytes(Encoding.Raw, PublicFormat.Raw))
    PUB_VERIFY.write_bytes(pub.public_bytes(Encoding.Raw, PublicFormat.Raw))

    print(f"OK WROTE {PRIV}")
    print(f"OK WROTE {PUB}")
    print(f"OK WROTE {PUB_VERIFY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())