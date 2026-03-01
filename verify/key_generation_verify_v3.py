import json
import sys

MANIFEST = "phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json"

def main():
    try:
        with open(MANIFEST, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print("KEY MANIFEST LOAD FAIL:", e)
        sys.exit(1)

    if "current_generation" not in data:
        print("KEY MANIFEST FAIL: missing current_generation")
        sys.exit(1)

    gens = data.get("generations", [])
    if not gens:
        print("KEY MANIFEST FAIL: no generations defined")
        sys.exit(1)

    current = data["current_generation"]
    active = [g for g in gens if g.get("status") == "active"]

    if len(active) != 1:
        print("KEY MANIFEST FAIL: multiple or zero active generations")
        sys.exit(1)

    if active[0].get("generation") != current:
        print("KEY MANIFEST FAIL: active generation mismatch")
        sys.exit(1)

    print("KEY GENERATION STRUCTURE PASS")

if __name__ == "__main__":
    main()
