from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parents[2]

def main():
    # NOTE: outbox path must not depend on current working directory
    outbox_dir = BASE_DIR / "outbox"

    # NOTE: placeholder - keep existing behavior wiring minimal for Phase17-Pre
    print(str(outbox_dir))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
