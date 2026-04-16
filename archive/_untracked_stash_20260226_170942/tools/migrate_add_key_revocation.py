import os
import sys
import sqlite3
from datetime import datetime, timezone

DB_PATH_DEFAULT = r"audit\ed25519\audit.db"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS key_revocation (
        key_id TEXT PRIMARY KEY,
        revoked_at TEXT NOT NULL,
        reason_code TEXT NOT NULL,
        reason_text TEXT,
        revoked_by TEXT NOT NULL,
        audit_event_id TEXT
    )
    """.strip(),
    """
    CREATE INDEX IF NOT EXISTS idx_key_revocation_revoked_at
    ON key_revocation(revoked_at)
    """.strip(),
]

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def table_exists(cur, name):
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None

def get_schema_version_row(cur, schema_name):
    return cur.execute(
        "SELECT schema_name, version FROM schema_versions WHERE schema_name=?",
        (schema_name,),
    ).fetchone()

def get_max_version(cur):
    row = cur.execute("SELECT MAX(version) FROM schema_versions").fetchone()
    return int(row[0]) if row and row[0] is not None else 0

def upsert_schema_version(cur, schema_name, note):
    applied_at = utc_now_iso()

    row = get_schema_version_row(cur, schema_name)
    if row is None:
        next_ver = get_max_version(cur) + 1
        cur.execute(
            "INSERT INTO schema_versions(schema_name, version, applied_at, note) VALUES(?,?,?,?)",
            (schema_name, next_ver, applied_at, note),
        )
        return ("INSERT", schema_name, next_ver, applied_at, note)

    current_ver = int(row[1])
    next_ver = current_ver + 1
    cur.execute(
        "UPDATE schema_versions SET version=?, applied_at=?, note=? WHERE schema_name=?",
        (next_ver, applied_at, note, schema_name),
    )
    return ("UPDATE", schema_name, next_ver, applied_at, note)

def main():
    db_path = DB_PATH_DEFAULT
    if len(sys.argv) >= 2:
        db_path = sys.argv[1]

    if not os.path.exists(db_path):
        print("DB NOT FOUND:", db_path, file=sys.stderr)
        return 1

    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        cur = con.cursor()

        if not table_exists(cur, "schema_versions"):
            print("ERROR: schema_versions not found. DB is not an audit ledger DB.", file=sys.stderr)
            return 2

        existed = table_exists(cur, "key_revocation")

        for sql in DDL:
            cur.execute(sql)

        action = None
        if not existed:
            action = upsert_schema_version(
                cur,
                "mocka.audit",
                "add key_revocation table",
            )

        con.commit()

        print("OK: key_revocation ensured")
        print("EXISTED:", existed)
        if action:
            print("SCHEMA_VERSION:", action)
        else:
            print("SCHEMA_VERSION: unchanged (table already existed)")
        return 0

    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())