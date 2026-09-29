#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path

db_path = Path('data/mocka_events.db')
if not db_path.exists():
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("=== Database Tables ===")
print(', '.join(sorted(tables)))

# Check key tables for audit
print("\n=== Key Tables for Audit ===")

for table_name in ['authorization_state', 'events', 'integrity_classifications']:
    if table_name in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"{table_name}: {count} rows")

        if table_name == 'authorization_state':
            cur.execute(f"SELECT decision_id, status, granted_at FROM {table_name} ORDER BY granted_at DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                print(f"  Latest: decision_id={row[0]}, status={row[1]}, granted_at={row[2]}")

        if table_name == 'events':
            cur.execute(f"SELECT event_id, title, when_ts FROM {table_name} ORDER BY when_ts DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                print(f"  Latest: event_id={row[0]}, title={row[1]}, when_ts={row[2]}")
    else:
        print(f"{table_name}: NOT FOUND")

conn.close()
