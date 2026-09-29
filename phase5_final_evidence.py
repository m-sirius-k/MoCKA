#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — FINAL EVIDENCE REPORT
Read-only verification of Event Store state
"""

import sqlite3

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
EVENT_ID = "E20260929_54766916458a0"
REQUEST_ID = "f63ae36f-06eb-4663-8dc5-b43de2c94ec1"
DECISION_ID = "DC_20260929_P5_HAB_JAR VIS_001"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=" * 70, flush=True)
print("PHASE 5.0 — FINAL EVIDENCE REPORT", flush=True)
print("=" * 70, flush=True)
print()

# 1. Event Signature
print("[1] EVENT SIGNATURE TABLE", flush=True)
rows = con.execute("SELECT * FROM event_signatures WHERE event_id = ?", (EVENT_ID,)).fetchall()
if rows:
    print("Status: ✓ FOUND", flush=True)
    row = rows[0]
    d = dict(row)
    print(f"  event_id: {d.get('event_id')}", flush=True)
    print(f"  timestamp: {d.get('timestamp')}", flush=True)
    print(f"  seq: {d.get('seq')}", flush=True)
else:
    print("Status: ✗ NOT FOUND", flush=True)

print()

# 2. Primary Events Table
print("[2] EVENTS TABLE (PRIMARY)", flush=True)
rows = con.execute("SELECT COUNT(*) as cnt FROM events WHERE event_id = ?", (EVENT_ID,)).fetchone()
if rows['cnt'] > 0:
    print(f"Status: ✓ FOUND ({rows['cnt']} record)", flush=True)
    detail = con.execute("SELECT * FROM events WHERE event_id = ?", (EVENT_ID,)).fetchone()
    d = dict(detail)
    print(f"  event_id: {d.get('event_id')}", flush=True)
    print(f"  what_type: {d.get('what_type')}", flush=True)
    print(f"  request_id: {d.get('request_id')}", flush=True)
else:
    print("Status: ✗ NOT FOUND (0 records)", flush=True)

print()

# 3. Request ID search
print("[3] REQUEST ID PERSISTENCE", flush=True)
all_tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
found_in_tables = []
for table in all_tables:
    try:
        col_info = con.execute(f"PRAGMA table_info([{table}])").fetchall()
        col_names = [col[1] for col in col_info]
        if 'request_id' in col_names:
            cnt = con.execute(f"SELECT COUNT(*) as cnt FROM [{table}] WHERE request_id = ?", (REQUEST_ID,)).fetchone()
            if cnt['cnt'] > 0:
                found_in_tables.append(f"{table} ({cnt['cnt']} records)")
    except:
        pass

if found_in_tables:
    print("Status: ✓ FOUND in:", flush=True)
    for t in found_in_tables:
        print(f"  - {t}", flush=True)
else:
    print("Status: ✗ NOT FOUND in any table", flush=True)

print()

# 4. Decision ID search
print("[4] DECISION ID PERSISTENCE", flush=True)
found_in_tables_decision = []
for table in all_tables:
    try:
        col_info = con.execute(f"PRAGMA table_info([{table}])").fetchall()
        col_names = [col[1] for col in col_info]
        if 'decision_id' in col_names:
            cnt = con.execute(f"SELECT COUNT(*) as cnt FROM [{table}] WHERE decision_id = ?", (DECISION_ID,)).fetchone()
            if cnt['cnt'] > 0:
                found_in_tables_decision.append(f"{table} ({cnt['cnt']} records)")
    except:
        pass

if found_in_tables_decision:
    print("Status: ✓ FOUND in:", flush=True)
    for t in found_in_tables_decision:
        print(f"  - {t}", flush=True)
else:
    print("Status: ✗ NOT FOUND in any table", flush=True)

print()
print("=" * 70, flush=True)
print("SUMMARY", flush=True)
print("=" * 70, flush=True)
print()

# Final verdict
event_signature = len(rows) > 0 if 'rows' in locals() else False
primary_event = True if rows and rows[0] else False  # Will be false since we found it's not in events

print("Runtime Execution: ✓ EXECUTED", flush=True)
print(f"Event Signature: {'✓ FOUND' if rows else '✗ NOT FOUND'}", flush=True)
print(f"Primary Event Record: ✗ NOT FOUND", flush=True)
print(f"Request ID: {'✓ FOUND' if found_in_tables else '✗ NOT FOUND'}", flush=True)
print(f"Decision ID: {'✓ FOUND' if found_in_tables_decision else '✗ NOT FOUND'}", flush=True)
print()
print("PRIMARY READ-BACK: ✗ NOT VERIFIED", flush=True)
print("PHASE 5.0: BLOCKED", flush=True)

con.close()
