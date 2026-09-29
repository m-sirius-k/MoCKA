import sqlite3
from pathlib import Path

DB = r'C:\Users\sirok\MoCKA\data\mocka_events.db'

# Step 1: Verify current schema
print("=== STEP 1: Current Schema ===")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()
schema = cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()[0]
print(schema)
con.close()

# Step 2: ALTER TABLE - recreate with 'orchestra_lineage' in allowed list
print("\n=== STEP 2: Backup and Modify ===")

# Connect with write access
con = sqlite3.connect(DB)
cur = con.cursor()

try:
    # Get all data from events
    print("  Backing up events table...")
    all_events = cur.execute("SELECT * FROM events").fetchall()
    event_cols = [d[0] for d in cur.description]
    print(f"  Event count: {len(all_events)}")

    # Rename old table
    cur.execute("ALTER TABLE events RENAME TO events_backup")
    print("  Renamed: events → events_backup")

    # Create new table with updated CHECK constraint
    new_schema = schema.replace(
        "_source TEXT NOT NULL CHECK (_source IN ('buffered', 'caliber_server', 'csv_legacy', 'csv_migration', 'direct_allowed:bootstrap', 'direct_allowed:maintenance', 'direct_allowed:migration', 'direct_allowed:recovery', 'direct_allowed:restore', 'direct_violation', 'gpt_handoff_20260509', 'legacy', 'live', 'new'))",
        "_source TEXT NOT NULL CHECK (_source IN ('buffered', 'caliber_server', 'csv_legacy', 'csv_migration', 'direct_allowed:bootstrap', 'direct_allowed:maintenance', 'direct_allowed:migration', 'direct_allowed:recovery', 'direct_allowed:restore', 'direct_violation', 'gpt_handoff_20260509', 'legacy', 'live', 'new', 'orchestra_lineage'))"
    )

    cur.execute(new_schema)
    print("  Created new events table with 'orchestra_lineage' in CHECK constraint")

    # Copy data back
    placeholders = ','.join(['?' for _ in event_cols])
    cols_str = ','.join(event_cols)
    cur.execute(f"INSERT INTO events ({cols_str}) SELECT {cols_str} FROM events_backup")
    print(f"  Copied {len(all_events)} rows back to events")

    # Drop backup
    cur.execute("DROP TABLE events_backup")
    print("  Dropped events_backup")

    con.commit()
    print("  COMMIT successful")

except Exception as e:
    con.rollback()
    print(f"  ERROR: {e}")
    raise
finally:
    con.close()

# Step 3: Verify new schema
print("\n=== STEP 3: Verify New Schema ===")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()
new_schema_verified = cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()[0]
if 'orchestra_lineage' in new_schema_verified:
    print("  ✓ 'orchestra_lineage' successfully added to CHECK constraint")
else:
    print("  ✗ 'orchestra_lineage' NOT found in new schema")
    print("\nNew schema:")
    print(new_schema_verified)
con.close()

print("\n=== COMPLETE ===")
print("Remediation A (minimal implementation) complete")
print("Ready for: Runtime execution → Event Store Read-Back")
