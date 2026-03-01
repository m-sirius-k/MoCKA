import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("phase3_key_policy/KEY_HISTORY_LOG_v3.jsonl")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def get_previous_event_hash():
    if not LOG_PATH.exists():
        return ""
    lines = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return ""
    last = json.loads(lines[-1])
    return last.get("event_sha256", "")

def append_event(event_type: str, generation_id: str, anchor_sha256: str):
    event = {
        "event_type": event_type,
        "generation_id": generation_id,
        "anchor_sha256": anchor_sha256,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "previous_event_sha256": get_previous_event_hash()
    }

    event_bytes = json.dumps(event, sort_keys=True).encode("utf-8")
    event["event_sha256"] = sha256_hex(event_bytes)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

    print("APPEND OK")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python key_history_append_v3.py <event_type> <generation_id> <anchor_sha256>")
        sys.exit(1)

    append_event(sys.argv[1], sys.argv[2], sys.argv[3])