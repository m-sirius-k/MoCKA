# -*- coding: utf-8 -*-

"""
MoCKA Safe Edit v0.1

Role:
    File integrity boundary for AI-assisted editing.

Functions:
    - Path normalization
    - UTF-8 validation
    - BOM removal
    - Backup creation
    - SHA-256 sealing
"""

from pathlib import Path
import hashlib
import shutil
from datetime import datetime, timezone
import sys


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_edit(path_str: str):

    target = Path(path_str).resolve()

    if not target.exists():
        raise FileNotFoundError(target)

    print("TARGET:")
    print(target)

    before_hash = sha256(target)

    backup = target.with_suffix(
        target.suffix + ".bak_" +
        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )

    shutil.copy2(target, backup)

    raw = target.read_text(
        encoding="utf-8-sig"
    )

    target.write_text(
        raw.rstrip() + "\n",
        encoding="utf-8"
    )

    after_hash = sha256(target)

    print("")
    print("BACKUP:")
    print(backup)

    print("")
    print("SHA256 BEFORE:")
    print(before_hash)

    print("")
    print("SHA256 AFTER:")
    print(after_hash)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "usage: python safe_edit.py <file>"
        )
        sys.exit(1)

    safe_edit(sys.argv[1])
