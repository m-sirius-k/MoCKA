#!/usr/bin/env python
import sqlite3
import sys
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'mocka_events.db'
print(f"Database path: {db_path}")
print(f"Exists: {db_path.exists()}")

if not db_path.exists():
    print("ERROR: Database file not found")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

try:
    # Check tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\nTables ({len(tables)}):")
    for t in tables:
        print(f"  - {t['name']}")

    # Check events table
    count = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    print(f"\nTotal events: {count}")

    # Check recent events
    print("\nRecent events (last 5):")
    recent = conn.execute(
        'SELECT event_id, what_type, when_ts FROM events ORDER BY when_ts DESC LIMIT 5'
    ).fetchall()

    for i, row in enumerate(recent, 1):
        print(f"  {i}. {row['event_id']} | {row['what_type']} | {row['when_ts']}")

    # Check for audit type
    audit_count = conn.execute("SELECT COUNT(*) FROM events WHERE what_type='audit'").fetchone()[0]
    print(f"\nEvents with what_type='audit': {audit_count}")

    # Check for incident type
    incident_count = conn.execute("SELECT COUNT(*) FROM events WHERE what_type='incident'").fetchone()[0]
    print(f"Events with what_type='incident': {incident_count}")

finally:
    conn.close()
