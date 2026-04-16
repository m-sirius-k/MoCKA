import sqlite3
import sys

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
TIP_PATH = r"C:\Users\sirok\MoCKA\audit\last_event_id.txt"


def main():
    with open(TIP_PATH, "r", encoding="utf-8") as f:
        tip = f.read().strip()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT event_id FROM audit_ledger_event WHERE event_id = ?",
        (tip,)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        print("OK: TIP verified in DB ledger")
        sys.exit(0)
    else:
        print("TIP NOT FOUND IN DB ledger:", tip)
        sys.exit(1)


if __name__ == "__main__":
    main()