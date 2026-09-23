#!/usr/bin/env python
"""Check existing DB schema for idempotency-related tables"""
import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db")

if not db_path.exists():
    print("DB file does not exist yet (will be created on first use)")
    exit(0)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 70)
print("EXISTING TABLES IN mocka_events.db")
print("=" * 70)

for (table_name,) in tables:
    print(f"\n--- {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    for col_id, col_name, col_type, not_null, dflt_value, pk in cols:
        pk_marker = " [PK]" if pk else ""
        print(f"  {col_name:30} {col_type:15}{pk_marker}")

print("\n" + "=" * 70)
print("SEARCH RESULTS")
print("=" * 70)

# Check for idempotency-related tables
idempotency_tables = [t for (t,) in tables if 'idempotency' in t.lower() or 'dedup' in t.lower() or 'request' in t.lower()]
if idempotency_tables:
    print(f"\nIdempotency/dedup/request tables found:")
    for t in idempotency_tables:
        print(f"  - {t}")
else:
    print("\nNo idempotency/dedup/request tables found in existing schema")

# Check for gate_idempotency specifically
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gate_idempotency'")
if cursor.fetchone():
    print("\n✓ gate_idempotency table EXISTS")
else:
    print("\n✗ gate_idempotency table DOES NOT exist")

# Check for request_executions specifically
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='request_executions'")
if cursor.fetchone():
    print("✓ request_executions table EXISTS")
    cursor.execute("PRAGMA table_info(request_executions)")
    cols = cursor.fetchall()
    print("  Schema:")
    for col_id, col_name, col_type, not_null, dflt_value, pk in cols:
        pk_marker = " [PK]" if pk else ""
        print(f"    {col_name:30} {col_type:15}{pk_marker}")
else:
    print("✗ request_executions table DOES NOT exist")

conn.close()
