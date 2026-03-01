import json
import hashlib
from pathlib import Path
import sys

LOG_PATH = Path("phase3_key_policy/KEY_HISTORY_LOG_v3.jsonl")

# 譌｢縺ｫ螻･豁ｴ縺ｫ蜈･縺｣縺ｦ縺励∪縺｣縺滄㍾隍・う繝吶Φ繝医ｒ縲∽ｾ句､悶→縺励※譏守､ｺ逧・↓險ｱ蜿ｯ縺吶ｋ
# 縺薙％縺ｫ蜈･縺｣縺ｦ縺・↑縺・㍾隍・・蜊ｳ FAIL・亥宛蠎ｦ縺ｨ縺励※遖∵ｭ｢・・
LEGACY_DUPLICATE_ALLOWLIST = {
    "0933ad8d851ddf50ff8d2a7cd13a84a287333258da603bb65c1f6cafb44ea72d",
}

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
    seen_keys: set[tuple[str, str]] = set()

    for idx, line in enumerate(lines, start=1):
        try:
            event = json.loads(line)
        except Exception as e:
            fail(f"invalid json at line {idx}: {e}")

        stored_hash = event.get("event_sha256", "")
        if not stored_hash:
            fail(f"missing event_sha256 at line {idx}")

        # 騾｣骼匁､懆ｨｼ
        expected_prev = previous_hash
        actual_prev = event.get("previous_event_sha256", "")
        if actual_prev != expected_prev:
            fail(f"chain broken at line {idx}: expected previous_event_sha256={expected_prev} got {actual_prev}")

        # 繝上ャ繧ｷ繝･蜀崎ｨ育ｮ嶺ｸ閾ｴ
        event_copy = dict(event)
        if "event_sha256" in event_copy:
            del event_copy["event_sha256"]

        recalculated = sha256_hex(json.dumps(event_copy, sort_keys=True).encode("utf-8"))
        if recalculated != stored_hash:
            fail(f"hash mismatch at line {idx}: recalculated={recalculated} stored={stored_hash}")

        # 驥崎､・､懃衍・亥宛蠎ｦ遖∵ｭ｢縲√◆縺縺・allowlist 縺ｯ險ｱ蜿ｯ・・
        event_type = event.get("event_type", "")
        generation_id = event.get("generation_id", "")
        if not event_type or not generation_id:
            fail(f"missing event_type or generation_id at line {idx}")

        key = (event_type, generation_id)
        if key in seen_keys:
            if stored_hash not in LEGACY_DUPLICATE_ALLOWLIST:
                fail(f"duplicate event detected at line {idx}: key={key} event_sha256={stored_hash}")
        else:
            seen_keys.add(key)

        previous_hash = stored_hash

    print("KEY HISTORY PASS")

if __name__ == "__main__":
    main()