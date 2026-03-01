import json
import hashlib
from pathlib import Path
import sys

ANCHOR_PATH = Path("phase3_key_policy/KEY_GENERATION_ANCHOR_v3.json")

def sha256_bytes(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def fail(msg: str) -> None:
    print(f"KEY ANCHOR FAIL: {msg}")
    sys.exit(1)

def main() -> None:
    if not ANCHOR_PATH.exists():
        fail("anchor missing")

    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))

    manifest_path = anchor.get("manifest_path", "")
    if not manifest_path:
        fail("manifest_path missing in anchor")

    manifest = Path(manifest_path)
    if not manifest.exists():
        fail(f"manifest not found: {manifest_path}")

    expected = anchor.get("manifest_sha256", "")
    if not expected:
        fail("manifest_sha256 missing in anchor")

    actual = sha256_bytes(manifest)

    if actual != expected:
        fail(f"manifest sha mismatch (actual={actual} expected={expected})")

    print("KEY ANCHOR PASS")

if __name__ == "__main__":
    main()