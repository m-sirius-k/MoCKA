import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# ★ここが重要（utf-8-sig）
with open("request.json", "r", encoding="utf-8-sig") as f:
    req = json.load(f)

payload = f"{req['fingerprint']}:{req['timestamp']}:{req['nonce']}"

signature = private_key.sign(payload.encode())

print(json.dumps({
    "payload": payload,
    "token": signature.hex()
}, indent=2))
