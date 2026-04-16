# FILE: C:\Users\sirok\MoCKA\_check_tables.py
import sqlite3
from pathlib import Path

db = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cur.fetchall():
    print(row[0])

conn.close()
