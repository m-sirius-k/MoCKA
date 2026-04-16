from __future__ import annotations

# NOTE: MoCKA Phase9-B
# NOTE: DB initializer for src.mocka_audit.db_schema
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m src.mocka_audit.init_audit_db

import os
import sys
from datetime import datetime, timezone

from . import db_schema

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def main(argv: list[str]) -> int:
    _ensure_parent_dir(DB_PATH)

    try:
        conn = db_schema.connect(DB_PATH)
        try:
            db_schema.apply_audit_schema_v1(
                conn,
                applied_at=_now_utc_iso(),
                note="init mocka.audit v1 (Phase9-B)",
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print("ERROR: schema apply failed")
        print("DB_PATH=" + DB_PATH)
        print(str(e))
        return 1

    if not os.path.isfile(DB_PATH):
        print("ERROR: DB file not created")
        return 2

    print("OK: audit.db initialized")
    print("DB_PATH=" + DB_PATH)
    print("SIZE_BYTES=" + str(os.path.getsize(DB_PATH)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))