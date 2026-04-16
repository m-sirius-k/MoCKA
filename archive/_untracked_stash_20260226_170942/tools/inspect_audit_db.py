import sqlite3
import json

db_path = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
SELECT id, event_content
FROM audit_ledger_event
WHERE event_type='daily_signature'
ORDER BY id DESC
LIMIT 1
""")

row = cur.fetchone()

if not row:
    print("NO daily_signature FOUND")
else:
    rowid, content = row
    payload = json.loads(content)
    print("ROWID:", rowid)
    print("message_canonical:", payload.get("message_canonical"))
    print("signature_hex (first32):", payload.get("signature_hex")[:32])

conn.close()