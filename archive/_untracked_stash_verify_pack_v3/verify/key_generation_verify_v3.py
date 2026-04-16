import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
MANIFEST = os.path.join(DATA, "KEY_GENERATION_MANIFEST_v3.json")


def fail(msg: str) -> int:
    print("status: FAIL")
    print("error: " + msg)
    return 1


def main() -> int:
    if not os.path.isfile(MANIFEST):
        return fail("missing manifest: " + MANIFEST)

    try:
        with open(MANIFEST, "r", encoding="utf-8-sig", newline="\n") as f:
            obj = json.load(f)
    except Exception as e:
        return fail("manifest load error: " + str(e))

    if not isinstance(obj, dict):
        return fail("manifest must be a JSON object (dict)")

    print("status: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
