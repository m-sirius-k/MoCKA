import json
import hashlib
import sys

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"
ANCHOR = "phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        raw = f.read()

    digest = sha256_bytes(raw.encode("utf-8"))

    try:
        with open(ANCHOR, "r", encoding="utf-8-sig") as f:
            a = json.load(f)
    except Exception as e:
        print("KEY ANCHOR LOAD FAIL:", e)
        sys.exit(1)

    expected = a.get("manifest_sha256")
    if expected != digest:
        print("KEY ANCHOR FAIL: manifest sha256 mismatch")
        print("expected:", expected)
        print("actual  :", digest)
        sys.exit(1)

    print("KEY ANCHOR PASS")

if __name__ == "__main__":
    main()
