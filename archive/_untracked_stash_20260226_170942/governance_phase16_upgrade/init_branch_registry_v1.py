# NOTE: init_branch_registry_v1.py (Phase16 T10)
# NOTE: Purpose: materialize Phase14.6 structural tables in governance.db.
# NOTE: Creates branch_registry and event_branch_map if missing.
# NOTE: Seeds a 'main' branch with classification='NORMAL' (NOT NULL).
# NOTE: Assigns all existing governance_ledger_event rows to 'main' if unmapped.

import sqlite3
from datetime import datetime, timezone

DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
GOV_TABLE = "governance_ledger_event"

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("BEGIN;")

cur.execute("""
CREATE TABLE IF NOT EXISTS branch_registry (
  branch_id TEXT PRIMARY KEY,
  classification TEXT NOT NULL,
  created_utc TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS event_branch_map (
  event_id TEXT PRIMARY KEY,
  branch_id TEXT NOT NULL,
  created_utc TEXT NOT NULL,
  FOREIGN KEY(branch_id) REFERENCES branch_registry(branch_id)
);
""")

# Seed main branch
cur.execute("SELECT COUNT(*) FROM branch_registry WHERE branch_id='main';")
if cur.fetchone()[0] == 0:
    cur.execute(
        "INSERT INTO branch_registry(branch_id, classification, created_utc) VALUES(?,?,?);",
        ("main", "NORMAL", utc_now()),
    )

# Map all events to main if missing
cur.execute(f"SELECT event_id FROM {GOV_TABLE};")
event_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT event_id FROM event_branch_map;")
mapped = set(r[0] for r in cur.fetchall())

to_add = [eid for eid in event_ids if eid not in mapped]
for eid in to_add:
    cur.execute(
        "INSERT INTO event_branch_map(event_id, branch_id, created_utc) VALUES(?,?,?);",
        (eid, "main", utc_now()),
    )

conn.commit()
conn.close()

print("OK: branch_registry/event_branch_map ready")
print("Mapped events to main:", len(to_add))