import sqlite3

db = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("""
SELECT id, event_type, prev_chain_hash, chain_hash
FROM audit_ledger_event
ORDER BY id DESC
LIMIT 5
""")

rows = cur.fetchall()

for r in rows:
    print(r)

conn.close()