import sqlite3
import shutil
import os
from datetime import datetime
import uuid

DB_PATH = "integrity.db"
BACKUP_PATH = "integrity_backup_pre_t2.db"

# 1. Backup
if not os.path.exists(BACKUP_PATH):
    shutil.copyfile(DB_PATH, BACKUP_PATH)
    print("Backup created.")
else:
    print("Backup already exists.")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 2. NULL backfill
cur.execute("SELECT COUNT(*) FROM attestation_log WHERE attestation_id IS NULL;")
null_count = cur.fetchone()[0]

if null_count > 0:
    print(f"Backfilling {null_count} NULL attestation_id rows...")
    cur.execute("SELECT rowid FROM attestation_log WHERE attestation_id IS NULL;")
    rows = cur.fetchall()
    for (rowid,) in rows:
        new_id = str(uuid.uuid4())
        cur.execute(
            "UPDATE attestation_log SET attestation_id=? WHERE rowid=?;",
            (new_id, rowid),
        )
else:
    print("No NULL attestation_id found.")

# 3. Rebuild table with constraints
cur.execute("BEGIN TRANSACTION;")

cur.execute("""
CREATE TABLE IF NOT EXISTS attestation_log_new (
  rowid INTEGER PRIMARY KEY,
  attestation_id TEXT NOT NULL UNIQUE,
  anchor_id TEXT NOT NULL,
  verifier TEXT NOT NULL,
  result TEXT NOT NULL,
  created_utc TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
""")

cur.execute("""
INSERT INTO attestation_log_new
(rowid, attestation_id, anchor_id, verifier, result, created_utc)
SELECT rowid, attestation_id, anchor_id, verifier, result, created_utc
FROM attestation_log;
""")

cur.execute("DROP TABLE attestation_log;")
cur.execute("ALTER TABLE attestation_log_new RENAME TO attestation_log;")

conn.commit()

# 4. Integrity check
cur.execute("PRAGMA integrity_check;")
result = cur.fetchone()[0]

print("Integrity check:", result)

conn.close()