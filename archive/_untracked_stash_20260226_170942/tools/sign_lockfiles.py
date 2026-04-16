import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

SOT_LOCK = ROOT / "src" / "source_of_truth.lock.json"
EXEC_LOCK = ROOT / "execution.lock.json"

PRIVKEY = ROOT / "audit" / "ed25519" / "keys" / "ed25519_private.key"

def sign_file(path: Path, privkey_bytes: bytes):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    data = path.read_bytes()
    sk = Ed25519PrivateKey.from_private_bytes(privkey_bytes)
    sig = sk.sign(data)
    path.with_suffix(path.suffix + ".sig").write_bytes(sig)

def sign_all() -> None:
    if not PRIVKEY.exists():
        raise RuntimeError("Private key missing")

    priv = PRIVKEY.read_bytes()
    if len(priv) != 32:
        raise RuntimeError("Invalid private key length")

    if SOT_LOCK.exists():
        sign_file(SOT_LOCK, priv)

    if EXEC_LOCK.exists():
        sign_file(EXEC_LOCK, priv)

if __name__ == "__main__":
    sign_all()
    print("OK: lockfiles signed")
