#!/usr/bin/env python3
import sqlite3
import json

db_path = 'data/mocka_events.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get schema
cur.execute("PRAGMA table_info(authorization_state)")
columns = cur.fetchall()
print("=== authorization_state schema ===")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get sample records
print("\n=== Sample records (latest 3) ===")
cur.execute("""
SELECT decision_id, status, scope, granted_at
FROM authorization_state
ORDER BY granted_at DESC
LIMIT 3
""")

for row in cur.fetchall():
    print(f"\ndecision_id: {row[0]}")
    print(f"  status: {row[1]}")
    print(f"  scope: {row[2]}")
    print(f"  granted_at: {row[3]}")

    # Try to parse scope as JSON
    if row[2]:
        try:
            scope_obj = json.loads(row[2])
            print(f"  scope (parsed): {scope_obj}")
        except:
            print(f"  scope (not JSON): {repr(row[2][:100])}")

conn.close()
