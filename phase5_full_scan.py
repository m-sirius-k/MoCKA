#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — FULL DATABASE SCAN
Search all tables for our identifiers
"""

import sqlite3
import json

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
REQUEST_ID = "f63ae36f-06eb-4663-8dc5-b43de2c94ec1"
DECISION_ID = "DC_20260929_P5_HAB_JARVIS_001"
EVENT_ID = "E20260929_54766916458a0"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("[PHASE 5.0 FULL DATABASE SCAN]", flush=True)
print(f"Looking for: request_id={REQUEST_ID}, event_id={EVENT_ID}", flush=True)
print()

# Get all tables
tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print(f"[TABLES TO SCAN] {len(tables)} tables", flush=True)

found_locations = []

for table in tables:
    try:
        col_info = con.execute(f"PRAGMA table_info([{table}])").fetchall()
        col_names = [col[1] for col in col_info]

        # Check if this table has searchable columns
        if "request_id" not in col_names and "event_id" not in col_names:
            continue

        # Search for our identifiers
        for col_name in ["request_id", "event_id"]:
            if col_name not in col_names:
                continue

            query = f"SELECT * FROM [{table}] WHERE [{col_name}] = ?"

            # Search request_id
            if col_name == "request_id":
                rows = con.execute(query, (REQUEST_ID,)).fetchall()
                if rows:
                    print(f"[FOUND REQUEST_ID in {table}.{col_name}]", flush=True)
                    for row in rows:
                        d = dict(row)
                        found_locations.append(f"{table}.{col_name}")
                        for key in list(d.keys())[:10]:  # Print first 10 fields
                            val = str(d[key])[:100]
                            print(f"  {key}: {val}", flush=True)
                        print()

            # Search event_id
            if col_name == "event_id":
                rows = con.execute(query, (EVENT_ID,)).fetchall()
                if rows:
                    print(f"[FOUND EVENT_ID in {table}.{col_name}]", flush=True)
                    for row in rows:
                        d = dict(row)
                        found_locations.append(f"{table}.{col_name}")
                        for key in list(d.keys())[:15]:  # Print first 15 fields
                            val = str(d[key])[:100]
                            print(f"  {key}: {val}", flush=True)
                        print()

    except Exception as e:
        pass  # Skip tables that error

print()
print("[SUMMARY]", flush=True)
if found_locations:
    print(f"✓ VERIFIED - Found in {len(found_locations)} location(s)", flush=True)
    for loc in found_locations:
        print(f"  - {loc}", flush=True)
else:
    print("✗ NOT VERIFIED - No matching records found", flush=True)

con.close()
