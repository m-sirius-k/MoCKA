import json
import hashlib
import sys
from datetime import datetime

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"
OUT = "phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        raw = f.read()
        data = json.loads(raw)

    digest = sha256_bytes(raw.encode("utf-8"))

    anchor = {
        "anchor_version": "v3",
        "manifest_path": MANIFEST,
        "manifest_sha256": digest,
        "anchored_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "current_generation": data.get("current_generation"),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(anchor, f, indent=2)

    print("KEY ANCHOR WRITTEN:", OUT)
    print("MANIFEST_SHA256:", digest)

if __name__ == "__main__":
    main()
