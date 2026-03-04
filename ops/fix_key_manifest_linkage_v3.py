import json
import sys
from datetime import datetime, timezone

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"
ANCHOR = "phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json"

def main():
    with open(ANCHOR, "r", encoding="utf-8-sig") as f:
        anchor = json.load(f)

    prev_anchor_hash = anchor.get("manifest_sha256")
    if not prev_anchor_hash:
        print("FIX FAIL: anchor missing manifest_sha256")
        sys.exit(1)

    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    current = data.get("current_generation")
    gens = data.get("generations", [])
    active = [g for g in gens if g.get("status") == "active"]

    if current is None or len(active) != 1:
        print("FIX FAIL: invalid manifest structure")
        sys.exit(1)

    g = active[0]

    # For generation >= 2, ensure linkage exists
    if current >= 2 and "previous_anchor_sha256" not in g:
        g["previous_anchor_sha256"] = prev_anchor_hash
        if "activated_at" not in g:
            g["activated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print("FIXED: injected previous_anchor_sha256 into active generation")
    else:
        print("NOOP: linkage already present or generation < 2")

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("PREV_ANCHOR_SHA256:", prev_anchor_hash)

if __name__ == "__main__":
    main()
