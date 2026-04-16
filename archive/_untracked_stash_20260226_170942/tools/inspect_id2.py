import sqlite3, json

db = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT event_content FROM audit_ledger_event WHERE id=2")
row = cur.fetchone()

payload = json.loads(row[0])
print("message_canonical:", payload["message_canonical"])
print("signature_hex:", payload["signature_hex"][:32])

conn.close()