import os
import sqlite3
import sys

NOTE = "Phase14 record orphans into branch_registry (write-once evidence)"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

TIP = "33cedbb94b557e08c1babf10006f288c112e26b2ecd4cb563458ff632f3b07d9"

ORPHANS = [
    ("fd58dcfa2f987814ec70658b559b9e4fbabd2842a01d44f4cb0acd22df17e646", "GENESIS"),
    ("43a48e0cec2b8cba2f3b955f048223e1d5756784d64cdb5df40229592c96df2b", "fd58dcfa2f987814ec70658b559b9e4fbabd2842a01d44f4cb0acd22df17e646"),
]

RAW_STDOUT_NOTE = """NOTE: Phase14 orphan detection tool (write-once evidence generator)
DB: C:\\Users\\sirok\\MoCKA\\audit\\ed25519\\audit.db
LEDGER_TABLE: audit_ledger_event
TIP: 33cedbb94b557e08c1babf10006f288c112e26b2ecd4cb563458ff632f3b07d9
TOTAL_EVENTS: 31
REACHABLE_COUNT: 30
ORPHAN_COUNT: 2

ORPHANS:
 - 43a48e0cec2b8cba2f3b955f048223e1d5756784d64cdb5df40229592c96df2b prev= fd58dcfa2f987814ec70658b559b9e4fbabd2842a01d44f4cb0acd22df17e646
 - fd58dcfa2f987814ec70658b559b9e4fbabd2842a01d44f4cb0acd22df17e646 prev= GENESIS
"""

def utc_now(conn):
    cur = conn.cursor()
    cur.execute("SELECT strftime('%Y-%m-%d %H:%M:%S','now');")
    return cur.fetchone()[0]

def ensure_table(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='branch_registry';")
    if not cur.fetchone():
        raise RuntimeError("branch_registry table not found. Run tools/phase14_init_branch_registry.py first.")

def main():
    if not os.path.exists(DB):
        print("ERROR: db not found:", DB)
        return 2

    conn = sqlite3.connect(DB)
    try:
        ensure_table(conn)
        ts = utc_now(conn)

        for orphan_id, orphan_prev in ORPHANS:
            conn.execute(
                """
                INSERT INTO branch_registry(
                    created_utc, tip_event_id, orphan_event_id, orphan_prev_id, classification, note
                ) VALUES(?,?,?,?,?,?)
                """,
                (ts, TIP, orphan_id, orphan_prev, "orphan_detected", RAW_STDOUT_NOTE)
            )

        conn.commit()
        print("OK: recorded_orphans_count:", len(ORPHANS))
        print("TIP:", TIP)
        print("UTC:", ts)
        print("NOTE:", NOTE)
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
