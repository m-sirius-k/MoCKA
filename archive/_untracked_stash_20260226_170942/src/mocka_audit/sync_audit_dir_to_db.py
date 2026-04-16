r"""
MoCKA Phase10/11
Sync audit/*.json (reachable or not) into canonical SQLite audit DB.

Goals:
- Do not depend on verify_chain module internals (no BASE_DIR import).
- Single DB path resolution:
  1) env MOCKA_AUDIT_DB_PATH if set
  2) canonical path C:\Users\sirok\MoCKA\audit\ed25519\audit.db
- Insert events into audit_ledger_event using flexible column matching.
- Idempotent: same event_id will not duplicate (best-effort upsert).
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.mocka_audit.db_schema import LEDGER_TABLE, connect, ensure_audit_ledger_table

CANONICAL_DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
ENV_DB_PATH_KEY = "MOCKA_AUDIT_DB_PATH"


def resolve_db_path() -> str:
    env = os.environ.get(ENV_DB_PATH_KEY)
    if env and env.strip():
        return env
    return CANONICAL_DB_PATH


def resolve_repo_root() -> Path:
    # .../MoCKA/src/mocka_audit/sync_audit_dir_to_db.py -> parents[2] == .../MoCKA
    return Path(__file__).resolve().parents[2]


def resolve_audit_dir(repo_root: Path) -> Path:
    return repo_root / "audit"


def _table_columns(conn: sqlite3.Connection, table: str) -> Dict[str, Dict[str, Any]]:
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols: Dict[str, Dict[str, Any]] = {}
    for row in cur.fetchall():
        cols[str(row[1])] = {
            "cid": row[0],
            "name": row[1],
            "type": row[2],
            "notnull": row[3],
            "dflt_value": row[4],
            "pk": row[5],
        }
    return cols


def _insert_flexible(conn: sqlite3.Connection, table: str, values: Dict[str, Any]) -> None:
    cols = _table_columns(conn, table)
    usable = {k: v for k, v in values.items() if k in cols}
    if not usable:
        raise RuntimeError(f"No matching columns to insert into {table}")

    keys = list(usable.keys())
    placeholders = ",".join(["?"] * len(keys))
    sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders});"
    conn.execute(sql, [usable[k] for k in keys])


def _row_exists(conn: sqlite3.Connection, table: str, event_id: str) -> bool:
    # assumes event_id column exists (true for MoCKA ledger)
    cur = conn.execute(f"SELECT 1 FROM {table} WHERE event_id=? LIMIT 1;", (event_id,))
    return cur.fetchone() is not None


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract_fields(doc: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    # best-effort extraction, matches MoCKA event schema used elsewhere
    event_id = str(doc.get("event_id", "")).strip()
    prev_event_id = doc.get("prev_event_id")
    if prev_event_id is not None:
        prev_event_id = str(prev_event_id).strip()

    chain_hash = doc.get("chain_hash")
    if chain_hash is not None:
        chain_hash = str(chain_hash).strip()

    created_at = doc.get("created_at")
    if created_at is not None:
        created_at = str(created_at).strip()

    return event_id, prev_event_id, chain_hash, created_at


def main() -> None:
    repo_root = resolve_repo_root()
    audit_dir = resolve_audit_dir(repo_root)
    db_path = resolve_db_path()

    if not audit_dir.is_dir():
        raise SystemExit(f"MISSING audit dir: {audit_dir}")

    files: List[Path] = sorted(audit_dir.glob("*.json"))
    print("repo_root:", str(repo_root))
    print("audit_dir:", str(audit_dir))
    print("db_path:", db_path)
    print("files:", len(files))

    conn = connect(db_path)
    try:
        ensure_audit_ledger_table(conn)

        inserted = 0
        skipped = 0
        bad = 0

        for p in files:
            try:
                doc = _read_json(p)
                event_id, prev_event_id, chain_hash, created_at = _extract_fields(doc)
                if not event_id:
                    bad += 1
                    continue

                if _row_exists(conn, LEDGER_TABLE, event_id):
                    skipped += 1
                    continue

                payload_json = json.dumps(doc, ensure_ascii=True, separators=(",", ":"))
                candidate = {
                    "event_id": event_id,
                    "prev_event_id": prev_event_id,
                    "chain_hash": chain_hash,
                    "created_at": created_at,
                    "payload_json": payload_json,
                    "note": f"sync_from_file:{p.name}",
                }
                _insert_flexible(conn, LEDGER_TABLE, candidate)
                inserted += 1
            except Exception:
                bad += 1

        conn.commit()
        print("OK: sync complete")
        print("inserted:", inserted)
        print("skipped_existing:", skipped)
        print("bad_files:", bad)
    finally:
        conn.close()


if __name__ == "__main__":
    main()