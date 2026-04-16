from __future__ import annotations

# NOTE: MoCKA Phase9-B
# NOTE: Seed exactly one GENESIS row into audit_ledger_event.
# NOTE: Safe to re-run: it will not insert if GENESIS already exists.
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m src.mocka_audit.seed_db_genesis

import sys
from datetime import datetime, timezone

from . import db_schema
from .verify_chain import DB_PATH


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main(argv: list[str]) -> int:
    # NOTE: DB_PATH may be str or pathlib.Path depending on caller/module version.
    db_path_str = str(DB_PATH)

    conn = db_schema.connect(db_path_str)
    try:
        cur = conn.cursor()

        # NOTE: If any row already has previous_event_id='GENESIS', treat as seeded.
        cur.execute(
            f"SELECT COUNT(1) FROM {db_schema.LEDGER_TABLE} WHERE previous_event_id='GENESIS';"
        )
        n = int(cur.fetchone()[0] or 0)
        if n >= 1:
            print("OK: GENESIS already exists")
            print("DB_PATH=" + db_path_str)
            return 0

        event_id = "GENESIS"
        chain_hash = "GENESIS"
        previous_event_id = "GENESIS"
        event_content = '{"type":"GENESIS","note":"seeded by seed_db_genesis.py"}'
        created_at = _now_utc_iso()

        cur.execute(
            f"""
            INSERT INTO {db_schema.LEDGER_TABLE}
                (event_id, chain_hash, previous_event_id, event_content, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (event_id, chain_hash, previous_event_id, event_content, created_at),
        )
        conn.commit()

        print("OK: GENESIS inserted")
        print("DB_PATH=" + db_path_str)
        return 0

    except Exception as e:
        print("ERROR: seed genesis failed")
        print("DB_PATH=" + db_path_str)
        print(str(e))
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))