#!/usr/bin/env python3
import sqlite3

db = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

print("[EVENTS TABLE - ALL NOT NULL COLUMNS]", flush=True)
schema_rows = con.execute("PRAGMA table_info(events)").fetchall()
not_null_cols = [row for row in schema_rows if row[3] == 1]

if not_null_cols:
    print(f"Found {len(not_null_cols)} NOT NULL column(s):", flush=True)
    for row in not_null_cols:
        col_name, col_type = row[1], row[2]
        print(f"  {col_name}: {col_type}", flush=True)
else:
    print("No NOT NULL columns (except primary key)", flush=True)

print()
print("[PRIMARY KEY]", flush=True)
pk_cols = [row for row in schema_rows if row[5] == 1]
for row in pk_cols:
    print(f"  {row[1]}: {row[2]}", flush=True)

print()
print("[CRITICAL CHECK]", flush=True)
print("If _write() payload is missing ANY NOT NULL column,")
print("INSERT will fail with 'NOT NULL constraint failed'")
print("But INSERT OR IGNORE will silently continue.")
print()

# Now check what _write() actually does with the payload
print("[EXAMINING _write() BEHAVIOR]", flush=True)
print()
print("From event_gate.py line 46-80:")
print("  payload → row mapping")
print("  Empty strings → None conversion")
print("  INSERT OR IGNORE")
print()
print("Payload fields mapped to events columns:", flush=True)
print("  'when_ts':         payload.get('when_ts') or payload.get('when', '')")
print("  'who_actor':       payload.get('who_actor', '')")
print("  'what_type':       payload.get('what_type', '')")
print("  'where_component': payload.get('where_component', '')")
print("  'where_path':      payload.get('where_path', '')")
print("  'why_purpose':     payload.get('why_purpose', '')")
print("  'how_trigger':     payload.get('how_trigger', '')")
print()
print("All of these are optional in payload → '' in row → None after conversion")
print()
print("Only 'when_ts' is NOT NULL in events table schema.")
print("So if payload['when_ts'] is provided and non-empty, INSERT should succeed.")
print()

con.close()
