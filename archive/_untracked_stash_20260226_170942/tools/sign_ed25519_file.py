import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

def load_privkey(path: Path) -> Ed25519PrivateKey:
    raw = path.read_bytes()
    if len(raw) == 32:
        return Ed25519PrivateKey.from_private_bytes(raw)
    k = serialization.load_pem_private_key(raw, password=None)
    if not isinstance(k, Ed25519PrivateKey):
        raise TypeError("not ed25519 private key")
    return k

def main() -> int:
    if len(sys.argv) != 3:
        print("USAGE: python tools/sign_ed25519_file.py <input_file> <sig_out>")
        return 2

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    key_path = os.environ.get("MOCKA_PHASE16_PRIVKEY_PATH", "")
    if not key_path:
        print("ERR: env MOCKA_PHASE16_PRIVKEY_PATH not set")
        return 3

    kp = Path(key_path)
    if not kp.exists():
        print("ERR: privkey not found:", str(kp))
        return 4

    sk = load_privkey(kp)
    sig = sk.sign(in_path.read_bytes())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(sig)

    print("WROTE_SIG:", str(out_path))
    print("SIG_LEN:", len(sig))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
