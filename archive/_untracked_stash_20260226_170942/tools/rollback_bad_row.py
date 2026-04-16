import sqlite3

db = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("DELETE FROM audit_ledger_event WHERE id=6")

conn.commit()
conn.close()

print("Row 6 deleted.")