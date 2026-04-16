import sqlite3
import sys

DB_PATH = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
TIP_PATH = r"C:\Users\sirok\MoCKA\governance\last_governance_event_id.txt"

def main():
    with open(TIP_PATH, "r", encoding="utf-8") as f:
        tip = f.read().strip()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT event_id FROM governance_ledger_event WHERE event_id = ?", (tip,))
    row = cur.fetchone()
    conn.close()

    if row:
        print("OK: Governance TIP verified")
        sys.exit(0)
    else:
        print("Governance TIP NOT FOUND:", tip)
        sys.exit(1)

if __name__ == "__main__":
    main()
