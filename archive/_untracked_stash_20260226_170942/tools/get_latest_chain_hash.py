import sqlite3

db_path = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
SELECT chain_hash
FROM audit_ledger_event
ORDER BY id DESC
LIMIT 1
""")

row = cur.fetchone()

if row:
    print("LATEST_CHAIN_HASH:", row[0])
else:
    print("NO ROW FOUND")

conn.close()