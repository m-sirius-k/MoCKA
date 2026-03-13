from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
SAMPLE = BASE / "samples" / "revoked_key_used.json"

def canonical_text(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def main():
    obj = json.loads(SAMPLE.read_text(encoding="utf-8"))
    obj["signatures"][0]["key_id"] = "authority_a_v1"
    SAMPLE.write_text(canonical_text(obj) + "\n", encoding="utf-8")
    print("OK: revoked_key_used.json now uses authority_a_v1")

if __name__ == "__main__":
    main()