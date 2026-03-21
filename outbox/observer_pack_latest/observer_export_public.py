from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

with open("observer_private.pem","rb") as f:
    priv = serialization.load_pem_private_key(f.read(), password=None)

pub = priv.public_key()
pub_pem = pub.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open("observer_public.pem","wb") as f:
    f.write(pub_pem)

print("OBSERVER_PUBLIC_EXPORTED")
