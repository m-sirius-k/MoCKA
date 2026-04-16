from __future__ import annotations

# NOTE: MoCKA Phase9-B/10
# NOTE: Rebuild DB ledger strictly from file-chain JSON under audit\
# NOTE: This removes any fake GENESIS row and recreates rows in correct chain order.
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m src.mocka_audit.rebuild_db_from_file_chain

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from . import db_schema
from .verify_chain import BASE_DIR, AUDIT_DIR, DB_PATH, AuditFileRecord


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json_utf8sig(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _load_file_records(audit_dir: Path) -> Dict[str, AuditFileRecord]:
    by_id: Dict[str, AuditFileRecord] = {}
    for f in audit_dir.glob("*.json"):
        if f.name.lower() == "seal_values.json":
            continue
        try:
            obj = _read_json_utf8sig(f)
        except Exception:
            continue
        if "event_id" not in obj:
            continue
        rec = AuditFileRecord(
            event_id=obj["event_id"],
            chain_hash=obj["chain_hash"],
            previous_event_id=obj["previous_event_id"],
            event_content=obj["event_content"],
        )
        by_id[rec.event_id] = rec
    return by_id


def _chain_order_from_last(by_id: Dict[str, AuditFileRecord], last_event_id: str) -> List[AuditFileRecord]:
    if last_event_id not in by_id:
        raise ValueError("last_event_id not found in records: " + last_event_id)

    seq: List[AuditFileRecord] = []
    cur = last_event_id
    while True:
        r = by_id[cur]
        seq.append(r)
        if r.previous_event_id == "GENESIS":
            break
        if r.previous_event_id not in by_id:
            raise ValueError("missing previous_event_id: " + r.previous_event_id)
        cur = r.previous_event_id

    # seq is last->...->genesisFirst, so reverse to insert genesisFirst->...->last
    seq.reverse()
    return seq


def main(argv: list[str]) -> int:
    audit_dir = Path(AUDIT_DIR)
    db_path_str = str(DB_PATH)

    last_path = audit_dir / "last_event_id.txt"
    if not last_path.exists():
        print("ERROR: missing last_event_id.txt")
        print("LAST_PATH=" + str(last_path))
        return 2

    last_event_id = last_path.read_text(encoding="utf-8-sig").strip()

    by_id = _load_file_records(audit_dir)
    if not by_id:
        print("ERROR: no audit event json records")
        print("AUDIT_DIR=" + str(audit_dir))
        return 3

    seq = _chain_order_from_last(by_id, last_event_id)

    conn = db_schema.connect(db_path_str)
    try:
        cur = conn.cursor()

        # Ensure schema/table exists
        db_schema.ensure_schema_versions(conn)
        db_schema.ensure_audit_ledger_table(conn)

        # Hard reset ledger table
        cur.execute(f"DELETE FROM {db_schema.LEDGER_TABLE};")

        inserted = 0
        for r in seq:
            cur.execute(
                f"""
                INSERT INTO {db_schema.LEDGER_TABLE}
                    (event_id, chain_hash, previous_event_id, event_content, created_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (r.event_id, r.chain_hash, r.previous_event_id, r.event_content, _now_utc_iso()),
            )
            inserted += 1

        conn.commit()

        print("OK: DB rebuilt from file chain")
        print("AUDIT_DIR=" + str(audit_dir))
        print("DB_PATH=" + db_path_str)
        print("INSERTED=" + str(inserted))
        print("LAST_EVENT_ID=" + last_event_id)
        return 0

    except Exception as e:
        print("ERROR: rebuild failed")
        print(str(e))
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))