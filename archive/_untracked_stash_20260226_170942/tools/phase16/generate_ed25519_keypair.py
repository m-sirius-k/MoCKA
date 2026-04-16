from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import os

BASE_DIR = r"C:\Users\sirok\MoCKA\secrets\phase16"
os.makedirs(BASE_DIR, exist_ok=True)

private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

priv_path = os.path.join(BASE_DIR, "ed25519_private.pem")
pub_path = os.path.join(BASE_DIR, "ed25519_public.pem")

with open(priv_path, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

with open(pub_path, "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

print("OK")
print("PRIVATE:", priv_path)
print("PUBLIC :", pub_path)