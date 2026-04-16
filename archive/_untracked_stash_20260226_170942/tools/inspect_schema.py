import sqlite3

db_path = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info(audit_ledger_event);")
rows = cur.fetchall()

for r in rows:
    print(r)

conn.close()