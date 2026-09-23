#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

db_path = Path("data/mocka_events.db")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check if events table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
if not cur.fetchone():
    print("Events table not found")
    conn.close()
    exit(1)

print("=" * 80)
print("HAB Multi-AI Request Events Check")
print("=" * 80)

# Get schema
cur.execute("PRAGMA table_info(events)")
columns = cur.fetchall()
print("\nTable columns:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Get latest multi_ai_request events
print("\n" + "=" * 80)
print("Latest multi_ai_request events:")
print("=" * 80)

cur.execute("""
    SELECT event_id, title, short_summary, when_ts, what_type, free_note, where_component
    FROM events
    WHERE what_type = 'multi_ai_request'
    ORDER BY when_ts DESC
    LIMIT 10
""")

rows = cur.fetchall()
if rows:
    print(f"\nFound {len(rows)} multi_ai_request event(s):\n")
    for i, row in enumerate(rows, 1):
        print(f"[{i}] Event ID: {row[0]}")
        print(f"    Title: {row[1]}")
        print(f"    Summary: {row[2]}")
        print(f"    Timestamp: {row[3]}")
        print(f"    Type: {row[4]}")
        print(f"    Component: {row[6]}")
        print(f"    Note (request_id): {row[5]}")
        print()
else:
    print("No multi_ai_request events found")

# Also check for socket-related events
print("=" * 80)
print("Latest socket events (any type containing 'socket' or 'multi'):")
print("=" * 80)

cur.execute("""
    SELECT event_id, title, short_summary, when_ts, what_type
    FROM events
    WHERE what_type LIKE '%socket%' OR what_type LIKE '%multi%'
    ORDER BY when_ts DESC
    LIMIT 5
""")

rows = cur.fetchall()
if rows:
    print(f"\nFound {len(rows)} socket/multi event(s):\n")
    for row in rows:
        print(f"  {row[4]}: {row[1]} ({row[3]})")
else:
    print("No socket/multi events found")

# Check total event count by type
print("\n" + "=" * 80)
print("Event count by type:")
print("=" * 80)

cur.execute("""
    SELECT what_type, COUNT(*) as count
    FROM events
    GROUP BY what_type
    ORDER BY count DESC
    LIMIT 20
""")

for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
print("\nDatabase check complete.")
