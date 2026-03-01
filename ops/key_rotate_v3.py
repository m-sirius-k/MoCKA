import json
import sys
from datetime import datetime

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"

def main():
    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    current = data["current_generation"]
    new_generation = current + 1

    # deactivate old
    for g in data["generations"]:
        if g["generation"] == current:
            g["status"] = "retired"

    # add new
    data["generations"].append({
        "generation": new_generation,
        "status": "active",
        "activated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "previous_generation": current
    })

    data["current_generation"] = new_generation

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("KEY ROTATION COMPLETE:", current, "->", new_generation)

if __name__ == "__main__":
    main()
