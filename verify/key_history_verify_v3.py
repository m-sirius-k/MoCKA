
import json
import hashlib
from pathlib import Path
import sys

LOG_PATH = Path("phase3_key_policy/KEY_HISTORY_LOG_v3.jsonl")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fail(msg: str) -> None:
    print(f"KEY HISTORY FAIL: {msg}")
    sys.exit(1)

def main() -> None:
    if not LOG_PATH.exists():
        fail("log file missing")

    raw = LOG_PATH.read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines() if ln.strip()]

    if not lines:
        fail("log is empty")

    previous_hash = ""

    for idx, line in enumerate(lines, start=1):
        try:
            event = json.loads(line)
        except Exception as e:
            fail(f"invalid json at line {idx}: {e}")

        stored_hash = event.get("event_sha256", "")
        if not stored_hash:
            fail(f"missing event_sha256 at line {idx}")

        expected_prev = previous_hash
        actual_prev = event.get("previous_event_sha256", "")
        if actual_prev != expected_prev:
            fail(f"chain broken at line {idx}: expected previous_event_sha256={expected_prev} got {actual_prev}")

        event_copy = dict(event)
        if "event_sha256" in event_copy:
            del event_copy["event_sha256"]

        recalculated = sha256_hex(json.dumps(event_copy, sort_keys=True).encode("utf-8"))
        if recalculated != stored_hash:
            fail(f"hash mismatch at line {idx}: recalculated={recalculated} stored={stored_hash}")

        previous_hash = stored_hash

    print("KEY HISTORY PASS")

if __name__ == "__main__":
    main()