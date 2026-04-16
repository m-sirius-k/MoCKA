import hashlib
import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
MANIFEST = os.path.join(DATA, "KEY_GENERATION_MANIFEST_v3.json")
ANCHOR = os.path.join(DATA, "KEY_GENERATION_ANCHOR_v3.json")


def sha256_bytes(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fail(msg: str) -> int:
    print("status: FAIL")
    print("error: " + msg)
    return 1


def main() -> int:
    if not os.path.isfile(MANIFEST):
        return fail("missing manifest: " + MANIFEST)
    if not os.path.isfile(ANCHOR):
        return fail("missing anchor: " + ANCHOR)

    try:
        with open(ANCHOR, "r", encoding="utf-8-sig", newline="\n") as f:
            anchor = json.load(f)
    except Exception as e:
        return fail("anchor load error: " + str(e))

    if not isinstance(anchor, dict):
        return fail("anchor must be a JSON object (dict)")

    manifest_sha = sha256_bytes(MANIFEST)

    expected = None
    for k in ["manifest_sha256", "manifest_sha256_bytes", "manifest_sha256_hex", "sha256_manifest", "sha256"]:
        if k in anchor:
            expected = anchor.get(k)
            break

    if expected is None:
        return fail("anchor missing expected manifest sha field (manifest_sha256 etc)")

    if not isinstance(expected, str):
        return fail("expected sha must be string")

    expected = expected.strip().lower()
    if manifest_sha != expected:
        return fail("sha mismatch: expected=" + expected + " actual=" + manifest_sha)

    print("status: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
