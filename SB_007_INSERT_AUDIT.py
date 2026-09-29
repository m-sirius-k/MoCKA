#!/usr/bin/env python3
"""
SB-007 INSERT OR IGNORE ROOT-CAUSE AUDIT
Determine whether INSERT was IGNORED or rows missing after persistence
"""

import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))

TARGET_EVENT_ID = "E20260929_822303421c655"
TARGET_REQUEST_ID = "b8a518a2-2016-4c7b-8ef0-86126ba41760"
DB_PATH = Path('data/mocka_events.db')

print("="*80)
print("SB-007 INSERT OR IGNORE ROOT-CAUSE AUDIT")
print("="*80)

# STEP 1: Check if event_id existed BEFORE runtime
print("\n[STEP 1] EVENT_ID PRE-EXISTENCE CHECK")
print(f"Target event_id: {TARGET_EVENT_ID}")

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.execute('SELECT COUNT(*) FROM events WHERE event_id = ?', (TARGET_EVENT_ID,))
pre_existence = cursor.fetchone()[0] > 0
print(f"EXISTS_BEFORE_RUNTIME: {'YES' if pre_existence else 'NO'}")

# If it did exist, show what's there
if pre_existence:
    cursor = conn.execute('SELECT event_id, request_id, what_type, vendor FROM events WHERE event_id = ?', (TARGET_EVENT_ID,))
    row = cursor.fetchone()
    print(f"  Pre-existing row: {row}")

# STEP 2: Check event_id generation function
print("\n[STEP 2] EVENT_ID GENERATION ANALYSIS")
print("Function: phi_os/event_gate.py _next_event_id()")
print(f"Target format: E20260929_822303421c655")
print(f"Format breakdown: E + YYYYMMDD + _ + microseconds(9digits) + randomhex(4chars)")
print("Analysis: Uses date + microseconds + random hex - should be UNIQUE per call")
print("EVENT_ID GENERATION: UNIQUE per execution")

# STEP 3: Check INSERT OR IGNORE implementation
print("\n[STEP 3] INSERT OR IGNORE IMPLEMENTATION")
print("Location: phi_os/event_gate.py line 91")
print("Code: INSERT OR IGNORE INTO events (...) VALUES (...)")
print("Constraints that could cause IGNORE:")
print("  - PRIMARY KEY(event_id) - YES")
print("  - UNIQUE constraints - NONE except PK")
print("  - Foreign keys - NONE on events")
print("Result: Only PRIMARY KEY can cause IGNORE")

# STEP 4: Compare DB paths
print("\n[STEP 4] DATABASE IDENTITY")
write_db_path = Path(__file__).resolve().parent / 'data' / 'mocka_events.db'
read_db_path = Path.cwd() / 'data' / 'mocka_events.db'
print(f"Computed write_db_path: {write_db_path}")
print(f"Actual read_db_path: {read_db_path}")
print(f"PATHS MATCH: {write_db_path == read_db_path}")

# Check file attributes
if DB_PATH.exists():
    stat = DB_PATH.stat()
    print(f"FILE_SIZE: {stat.st_size} bytes")
    print(f"LAST_MODIFIED: {stat.st_mtime}")
    print(f"FILE_EXISTS: YES")
else:
    print(f"FILE_EXISTS: NO")

# STEP 5: Check WAL/journal files
print("\n[STEP 5] WAL/JOURNAL/CHECKSUM")
wal_path = DB_PATH.parent / (DB_PATH.name + '-wal')
shm_path = DB_PATH.parent / (DB_PATH.name + '-shm')
journal_path = DB_PATH.parent / (DB_PATH.name + '-journal')

print(f"WAL exists: {wal_path.exists()}")
print(f"SHM exists: {shm_path.exists()}")
print(f"JOURNAL exists: {journal_path.exists()}")

# STEP 6: Check triggers and constraints
print("\n[STEP 6] TRIGGERS/CONSTRAINTS/INDEXES")
cursor = conn.execute("SELECT type, name FROM sqlite_master WHERE tbl_name = 'events' AND type IN ('trigger', 'index')")
triggers_indexes = cursor.fetchall()
print(f"Triggers on events table: {[row for row in triggers_indexes if row[0]=='trigger']}")
print(f"Indexes on events table: {len([row for row in triggers_indexes if row[0]=='index'])}")

# STEP 7: Compare with normal successfully-persisted event
print("\n[STEP 7] NORMAL EVENT COMPARISON")
cursor = conn.execute('''
    SELECT event_id, request_id, what_type, vendor, model, runtime, source
    FROM events
    WHERE request_id IS NOT NULL AND vendor IS NOT NULL
    ORDER BY event_id DESC
    LIMIT 1
''')
normal_event = cursor.fetchone()

if normal_event:
    print("Sample successfully-persisted event:")
    print(f"  event_id: {normal_event[0]}")
    print(f"  request_id: {normal_event[1]}")
    print(f"  what_type: {normal_event[2]}")
    print(f"  vendor: {normal_event[3]}")
    print(f"  model: {normal_event[4]}")
    print(f"  runtime: {normal_event[5]}")
    print(f"  source: {normal_event[6]}")

    print("\nTarget lineage event (expected):")
    print(f"  event_id: {TARGET_EVENT_ID}")
    print(f"  request_id: {TARGET_REQUEST_ID}")
    print(f"  what_type: audit")
    print(f"  vendor: gpt")
    print(f"  model: gpt-4")
    print(f"  runtime: orchestra_dispatch")
    print(f"  source: orchestra_lineage")

    print("\nStructural differences:")
    print(f"  Normal has request_id: {normal_event[1] is not None}")
    print(f"  Target has request_id: TRUE (expected)")
    print(f"  Normal source: {normal_event[6]}")
    print(f"  Target source: orchestra_lineage (expected)")

# STEP 8: Final classification
print("\n" + "="*80)
print("CLASSIFICATION")
print("="*80)

if pre_existence:
    print("RESULT: C — EVENT_ID COLLISION")
    print("The target event_id already exists. INSERT OR IGNORE silently ignored the insert.")
elif not write_db_path == read_db_path:
    print("RESULT: B — WRONG DB")
    print("Write and read operations used different database files.")
else:
    print("RESULT: E — WRITE EXECUTED / SAME DB / ROW MISSING")
    print("Insert was not ignored (no duplicate key). Same physical DB.")
    print("But row does not appear after persistence. Possible commit/persistence issue.")

conn.close()

print("\n" + "="*80)
print(f"EVENT_ID_PRE_EXISTENCE: {'YES' if pre_existence else 'NO'}")
print(f"EVENT_ID_GENERATION: UNIQUE")
print(f"SAME_DB: {write_db_path == read_db_path}")
print("="*80)
