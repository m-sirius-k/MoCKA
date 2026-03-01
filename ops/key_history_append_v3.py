import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("phase3_key_policy/KEY_HISTORY_LOG_v3.jsonl")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_lines() -> list[str]:
    if not LOG_PATH.exists():
        return []
    raw = LOG_PATH.read_text(encoding="utf-8")
    return [ln for ln in raw.splitlines() if ln.strip()]

def get_previous_event_hash(lines: list[str]) -> str:
    if not lines:
        return ""
    last = json.loads(lines[-1])
    return last.get("event_sha256", "")

def already_exists(lines: list[str], event_type: str, generation_id: str) -> bool:
    for ln in lines:
        ev = json.loads(ln)
        if ev.get("event_type") == event_type and ev.get("generation_id") == generation_id:
            return True
    return False

def append_event(event_type: str, generation_id: str, anchor_sha256: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = read_lines()

    if already_exists(lines, event_type, generation_id):
        print("APPEND REJECT: duplicate (event_type,generation_id)")
        sys.exit(2)

    event = {
        "event_type": event_type,
        "generation_id": generation_id,
        "anchor_sha256": anchor_sha256,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "previous_event_sha256": get_previous_event_hash(lines),
    }

    event_bytes = json.dumps(event, sort_keys=True).encode("utf-8")
    event["event_sha256"] = sha256_hex(event_bytes)

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

    print("APPEND OK")

def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python key_history_append_v3.py <event_type> <generation_id> <anchor_sha256>")
        sys.exit(1)

    append_event(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()