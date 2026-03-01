import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_PATH = Path("phase3_key_policy/KEY_GENERATION_MANIFEST_v3.json")
ANCHOR_PATH = Path("phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json")

def sha256_hex(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def utc_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main() -> None:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"MANIFEST NOT FOUND: {MANIFEST_PATH}")

    manifest_sha = sha256_hex(MANIFEST_PATH)

    anchor = {
        "anchor_version": "v3",
        "manifest_path": str(MANIFEST_PATH).replace("\\", "/"),
        "manifest_sha256": manifest_sha,
        "anchored_at_utc": utc_z()
    }

    ANCHOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    ANCHOR_PATH.write_text(json.dumps(anchor, indent=2) + "\n", encoding="utf-8")

    print(f"KEY ANCHOR WRITTEN: {ANCHOR_PATH.as_posix()}")
    print(f"MANIFEST_SHA256: {manifest_sha}")

if __name__ == "__main__":
    main()