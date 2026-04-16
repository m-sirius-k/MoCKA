import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = r"C:\Users\sirok\MoCKA"

FILES = {
    "verify_all_py": r"verify\verify_all.py",
    "accept_outfield_pass_py": r"verify\accept_outfield_pass.py",
    "summary_matrix_json": r"acceptance\summary_matrix.json",
}

VERIFY_PACK_NAME = "mocka_phase17pre_verify_pack_20260225_032005.zip"
VERIFY_PACK_SHA256 = "A0221149435F18D7EEC1B63BB4E6059927DBF8F356FA8A1E17DF29CFAE115B78"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().upper()

manifest = {
    "phase": "Phase17-Pre",
    "freeze_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "verify_pack": {
        "zip_name": VERIFY_PACK_NAME,
        "sha256": VERIFY_PACK_SHA256,
    },
    "files": {}
}

for key, rel in FILES.items():
    path = os.path.join(ROOT, rel)
    manifest["files"][key] = {
        "path": rel,
        "sha256": sha256_file(path)
    }

out_path = os.path.join(ROOT, "freeze_manifest.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("FREEZE MANIFEST CREATED")
print(out_path)