import os
import sqlite3
import sys

NOTE = "Phase14 branch registry initializer"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS branch_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_utc TEXT NOT NULL,
        tip_event_id TEXT NOT NULL,
        orphan_event_id TEXT NOT NULL,
        orphan_prev_id TEXT,
        classification TEXT NOT NULL,
        note TEXT NOT NULL
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_branch_registry_tip
    ON branch_registry(tip_event_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_branch_registry_orphan
    ON branch_registry(orphan_event_id);
    """
]

def utc_now(conn):
    cur = conn.cursor()
    cur.execute("SELECT strftime('%Y-%m-%d %H:%M:%S','now');")
    return cur.fetchone()[0]

def main():
    if not os.path.exists(DB):
        print("ERROR: db not found:", DB)
        return 2

    conn = sqlite3.connect(DB)
    try:
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        conn.commit()

        ts = utc_now(conn)
        print("OK: branch_registry ready")
        print("DB:", DB)
        print("UTC:", ts)
        print("NOTE:", NOTE)
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
