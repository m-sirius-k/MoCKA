import os
import sqlite3
import sys

NOTE = "Phase14 orphan classification updater"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

VALID_CLASSES = {
    "historical_test",
    "operational_accident",
    "quarantined",
    "reintegrated"
}

def utc_now(conn):
    cur = conn.cursor()
    cur.execute("SELECT strftime('%Y-%m-%d %H:%M:%S','now');")
    return cur.fetchone()[0]

def main():
    if len(sys.argv) < 4:
        print("Usage: python phase14_update_classification.py <orphan_event_id> <new_classification> <reason_note>")
        return 1

    orphan_id = sys.argv[1]
    new_class = sys.argv[2]
    reason = sys.argv[3]

    if new_class not in VALID_CLASSES:
        print("ERROR: invalid classification")
        return 2

    if not os.path.exists(DB):
        print("ERROR: db not found:", DB)
        return 3

    conn = sqlite3.connect(DB)
    try:
        ts = utc_now(conn)
        conn.execute("""
            UPDATE branch_registry
            SET classification=?, note=note || '\nCLASS_UPDATE ' || ?
            WHERE orphan_event_id=?
        """, (new_class, reason, orphan_id))
        conn.commit()

        print("UPDATED:", orphan_id)
        print("NEW_CLASS:", new_class)
        print("UTC:", ts)
        print("NOTE:", NOTE)
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
