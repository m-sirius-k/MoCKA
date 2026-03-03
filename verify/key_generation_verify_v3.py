import json
import sys

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"

def main():
    with open(MANIFEST, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    gens = data.get("generations", [])
    current = data.get("current_generation")

    active = [g for g in gens if g.get("status") == "active"]

    if len(active) != 1:
        print("KEY MANIFEST FAIL: invalid active count")
        sys.exit(1)

    if active[0]["generation"] != current:
        print("KEY MANIFEST FAIL: active mismatch")
        sys.exit(1)

    for g in gens:
        if g["generation"] != current and g["status"] == "active":
            print("KEY MANIFEST FAIL: multiple active generations")
            sys.exit(1)

    print("KEY GENERATION STRUCTURE PASS")

if __name__ == "__main__":
    main()
