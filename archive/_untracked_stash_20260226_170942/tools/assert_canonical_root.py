import os
import sys

CANONICAL_ROOT = r"C:\Users\sirok\MoCKA"

def main() -> int:
    cwd = os.path.abspath(os.getcwd())
    root = os.path.abspath(CANONICAL_ROOT)

    if not (cwd == root or cwd.startswith(root + os.sep)):
        print("[PHASE9_BLOCK] non-canonical cwd")
        print("cwd:", cwd)
        print("expected_root:", root)
        return 2

    print("[OK] canonical cwd")
    print("cwd:", cwd)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
