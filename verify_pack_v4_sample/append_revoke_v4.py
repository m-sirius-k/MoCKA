from pathlib import Path
import json
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
REG = BASE / "KEY_REGISTRY_v4.jsonl"

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def canonical_line(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def main():
    if not REG.exists():
        raise SystemExit("KEY_REGISTRY_v4.jsonl not found")

    revoke = {
        "event_type": "revoke",
        "key_id": "authority_a_v1",
        "revoked_at": utc_now_iso(),
        "reason": "sample revoke for negative test"
    }

    with REG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(canonical_line(revoke) + "\n")

    print("OK: revoke appended for authority_a_v1")

if __name__ == "__main__":
    main()