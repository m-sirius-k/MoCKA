import sqlite3
import json

db_path = r"C:\Users\sirok\MoCKA\infield\phase11\db\knowledge.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
SELECT rowid, event_type, content
FROM audit_ledger_event
WHERE event_type = 'daily_signature'
ORDER BY rowid DESC
LIMIT 1
""")

row = cur.fetchone()

if not row:
    print("No daily_signature found")
else:
    rowid, event_type, content = row
    print("ROWID:", rowid)
    payload = json.loads(content)
    print("message_canonical:", payload.get("message_canonical"))
    print("signature_hex:", payload.get("signature_hex"))

conn.close()