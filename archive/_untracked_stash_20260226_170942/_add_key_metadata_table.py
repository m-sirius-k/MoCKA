import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS key_metadata (
    key_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT
)
""")

conn.commit()
conn.close()

print("KEY_METADATA_TABLE_READY")
