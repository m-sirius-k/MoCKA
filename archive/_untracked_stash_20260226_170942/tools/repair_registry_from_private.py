import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

BASE = Path(r"C:\Users\sirok\MoCKA")
REGISTRY_PATH = BASE / r"audit\key_registry.json"
PRIVATE_KEY_PATH = BASE / r"secrets\ed25519\ed25519_private.key"

raw_priv = PRIVATE_KEY_PATH.read_bytes()
if len(raw_priv) != 32:
    raise ValueError("Private key must be 32 bytes")

priv = ed25519.Ed25519PrivateKey.from_private_bytes(raw_priv)
pub = priv.public_key()

pub_pem = pub.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

pub_raw = pub.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

print("NEW PUBLIC RAW HEX:")
print(pub_raw.hex())
print()

ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_path = REGISTRY_PATH.with_name(
    REGISTRY_PATH.stem + ".bak_" + ts + REGISTRY_PATH.suffix
)

shutil.copy2(REGISTRY_PATH, backup_path)

print("Backup written to:")
print(backup_path)
print()

with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
    registry = json.load(f)

new_key_id = f"key_{ts}"

for k in registry["keys"]:
    if k["key_id"] == registry["active_key_id"]:
        k["status"] = "inactive"
        k["deactivated_at"] = ts

registry["keys"].append({
    "key_id": new_key_id,
    "public_key_pem": pub_pem,
    "status": "active",
    "activated_at": ts,
    "deactivated_at": None,
    "revocation_reason": None
})

registry["active_key_id"] = new_key_id

with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Registry updated.")
print("New active_key_id:", new_key_id)