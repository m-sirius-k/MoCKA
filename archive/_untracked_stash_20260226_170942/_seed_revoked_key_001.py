import sqlite3
from datetime import datetime, UTC
from pathlib import Path

DB = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")
now = datetime.now(UTC).isoformat()

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute(
    "INSERT OR REPLACE INTO key_metadata (key_id, status, valid_from, valid_to) VALUES (?, 'revoked', ?, ?)",
    ("test-key-001", now, now)
)

conn.commit()
conn.close()

print("SEEDED_REVOKED: test-key-001")
