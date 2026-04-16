import os
import sqlite3
import sys

NOTE = "Phase14 branch guard report (classification summary)"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

def main():
    if not os.path.exists(DB):
        print("ERROR: db not found:", DB)
        return 2

    conn = sqlite3.connect(DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='branch_registry';")
        if not cur.fetchone():
            print("ERROR: branch_registry not found")
            return 3

        print("NOTE:", NOTE)
        print("DB:", DB)
        print()

        cur.execute("""
            SELECT classification, COUNT(*)
            FROM branch_registry
            GROUP BY classification
            ORDER BY classification;
        """)
        print("COUNTS_BY_CLASS:")
        for c, n in cur.fetchall():
            print(" -", c, n)

        print()
        cur.execute("""
            SELECT created_utc, tip_event_id, orphan_event_id, orphan_prev_id, classification
            FROM branch_registry
            ORDER BY id DESC
            LIMIT 50;
        """)
        print("LAST_ROWS:")
        for r in cur.fetchall():
            print("ROW:", r)

        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
