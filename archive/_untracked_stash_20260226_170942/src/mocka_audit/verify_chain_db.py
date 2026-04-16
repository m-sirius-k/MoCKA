# FILE: C:\Users\sirok\MoCKA\src\mocka_audit\verify_chain_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")

def verify_chain():
    if not DB_PATH.exists():
        raise Exception("audit.db not found")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # created_at は TEXT（ISO形式）なので降順でOK
    cur.execute(
        "SELECT event_id, prev_event_id FROM audit_ledger_event "
        "ORDER BY created_at DESC LIMIT 1"
    )
    row = cur.fetchone()

    if not row:
        raise Exception("audit_ledger_event empty")

    tip = row[0]
    print(f"OK: TIP={tip}")

    current = tip
    length = 0

    while current:
        cur.execute(
            "SELECT prev_event_id FROM audit_ledger_event WHERE event_id=?",
            (current,)
        )
        r = cur.fetchone()

        if not r:
            print(f"WARN: missing event in DB: {current}")
            break

        current = r[0]
        length += 1

        if current == "GENESIS":
            break

    print(f"OK: reachable length={length}")
    conn.close()

if __name__ == "__main__":
    verify_chain()
