# C:\Users\sirok\MoCKA\tools\dump_verify_pubkey.py

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pathlib import Path

BASE = Path(r"C:\Users\sirok\MoCKA")

# verify_pack が参照している公開鍵をここで指定
# 必要に応じてファイル名を変更してください
pub_path = BASE / r"keys\ed25519_public_regenerated.pem"

if not pub_path.exists():
    raise FileNotFoundError(f"Public key not found: {pub_path}")

data = pub_path.read_bytes()

public_key = serialization.load_pem_public_key(data)

if not isinstance(public_key, ed25519.Ed25519PublicKey):
    raise TypeError("Not an Ed25519 public key")

raw = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

print("VERIFY SIDE PUBLIC RAW HEX:")
print(raw.hex())