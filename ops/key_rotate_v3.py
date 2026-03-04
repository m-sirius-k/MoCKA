import json
import hashlib
from datetime import datetime, timezone

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"
ANCHOR = "phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json"

def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        raw = f.read()
        return raw, json.loads(raw)

def load_anchor():
    with open(ANCHOR, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    _, data = load_manifest()
    anchor = load_anchor()

    current = data["current_generation"]
    new_generation = current + 1

    for g in data["generations"]:
        if g["generation"] == current:
            g["status"] = "retired"

    prev_anchor_hash = anchor.get("manifest_sha256")

    data["generations"].append({
        "generation": new_generation,
        "status": "active",
        "activated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "previous_generation": current,
        "previous_anchor_sha256": prev_anchor_hash
    })

    data["current_generation"] = new_generation

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("KEY ROTATION COMPLETE:", current, "->", new_generation)
    print("LINKED TO ANCHOR:", prev_anchor_hash)

if __name__ == "__main__":
    main()
