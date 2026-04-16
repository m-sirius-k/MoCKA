# FILE: C:\Users\sirok\MoCKA\_check_columns.py
import sqlite3
from pathlib import Path

db = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("PRAGMA table_info(audit_ledger_event);")
for row in cur.fetchall():
    print(row)

conn.close()
