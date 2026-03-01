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
        data = json.loads(raw)

    digest = sha256_bytes(raw.encode("utf-8"))

    with open(ANCHOR, "r", encoding="utf-8-sig") as f:
        anchor = json.load(f)

    if anchor.get("manifest_sha256") != digest:
        print("KEY ANCHOR FAIL: manifest sha mismatch")
        sys.exit(1)

    current = data.get("current_generation")
    gens = data.get("generations", [])

    active = [g for g in gens if g.get("status") == "active"]
    if len(active) != 1:
        print("KEY ANCHOR FAIL: invalid active count")
        sys.exit(1)

    g = active[0]

    if g.get("generation") != current:
        print("KEY ANCHOR FAIL: active mismatch")
        sys.exit(1)

    # if not first generation, ensure linkage field exists
    if current > 1:
        if "previous_anchor_sha256" not in g:
            print("KEY ANCHOR FAIL: missing previous_anchor_sha256")
            sys.exit(1)

    print("KEY ANCHOR PASS")

if __name__ == "__main__":
    main()
