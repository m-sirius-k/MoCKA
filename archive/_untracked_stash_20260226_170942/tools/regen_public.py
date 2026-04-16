# C:\Users\sirok\MoCKA\tools\regen_public.py

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pathlib import Path

BASE = Path(r"C:\Users\sirok\MoCKA")

priv_path = BASE / r"secrets\ed25519\ed25519_private.key"
out_pem_path = BASE / r"keys\ed25519_public_regenerated.pem"

if not priv_path.exists():
    raise FileNotFoundError(f"Private key not found: {priv_path}")

raw = priv_path.read_bytes()

if len(raw) != 32:
    raise ValueError(f"Private key must be 32 bytes. Actual: {len(raw)}")

private_key = ed25519.Ed25519PrivateKey.from_private_bytes(raw)
public_key = private_key.public_key()

# RAW 32byte 公開鍵
pub_raw = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

print("PUBLIC RAW HEX:")
print(pub_raw.hex())
print("")

# PEM形式保存
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

out_pem_path.write_bytes(pem)

print(f"PEM written to:")
print(out_pem_path)