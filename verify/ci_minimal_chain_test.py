import os
import sqlite3
import hashlib

DB = "ci_test.db"

def sha256(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()

def main():
    if os.path.exists(DB):
        os.remove(DB)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE ledger (
        id INTEGER PRIMARY KEY,
        payload TEXT,
        hash TEXT
    )
    """)

    payload = "ci-test-payload"
    h = sha256(payload.encode())

    cur.execute("INSERT INTO ledger (payload, hash) VALUES (?, ?)", (payload, h))
    conn.commit()

    # simple integrity check
    cur.execute("SELECT payload, hash FROM ledger WHERE id=1")
    p, stored = cur.fetchone()
    recalculated = sha256(p.encode())

    if recalculated != stored:
        print("CI TEST FAIL: hash mismatch")
        exit(1)

    print("CI TEST PASS")
    conn.close()
    os.remove(DB)

if __name__ == "__main__":
    main()
