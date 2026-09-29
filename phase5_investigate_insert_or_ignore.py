#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 ROOT CAUSE: Investigate INSERT OR IGNORE behavior
"""

import sqlite3

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
EVENT_ID = "E20260929_54766916458a0"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("[INVESTIGATING INSERT OR IGNORE BEHAVIOR]", flush=True)
print()

# Check if event_id exists in events table
count = con.execute("SELECT COUNT(*) as cnt FROM events WHERE event_id = ?", (EVENT_ID,)).fetchone()
print(f"Events table: Count for {EVENT_ID} = {count['cnt']}", flush=True)

# Check if event_id exists in event_signatures table
count_sig = con.execute("SELECT COUNT(*) as cnt FROM event_signatures WHERE event_id = ?", (EVENT_ID,)).fetchone()
print(f"Event signatures table: Count for {EVENT_ID} = {count_sig['cnt']}", flush=True)

print()
print("[CRITICAL HYPOTHESIS]", flush=True)
print("process_event() called", flush=True)
print("  ↓", flush=True)
print("_write() executes 'INSERT OR IGNORE INTO events' with event_id", flush=True)
print("  ↓", flush=True)
if count['cnt'] > 0:
    print("IF event_id EXISTS: INSERT does NOTHING (ignored)", flush=True)
else:
    print("IF event_id NOT EXISTS: INSERT succeeds", flush=True)
print("  ↓", flush=True)
print("sign_event() writes to event_signatures (always executes)", flush=True)
print()

# Check for events near timestamp
print("[CHECK: Events near timestamp 2026-09-29T06:32:19]", flush=True)
related = con.execute(
    "SELECT event_id, when_ts, what_type, request_id FROM events WHERE when_ts LIKE '2026-09-29T06:32:19%' LIMIT 10"
).fetchall()

if related:
    print(f"Found {len(related)} event(s):", flush=True)
    for row in related:
        print(f"  {row['event_id']}: {row['what_type']} | request_id={row['request_id']}", flush=True)
else:
    print("No events found near this timestamp", flush=True)

print()

# Check event_gate transaction behavior - look for failed inserts
print("[CHECK: Event records with NULL or ZERO request_id]", flush=True)
null_req = con.execute(
    "SELECT COUNT(*) as cnt FROM events WHERE event_id LIKE 'E20260929%' AND request_id IS NULL"
).fetchone()
print(f"Events on 2026-09-29 with NULL request_id: {null_req['cnt']}", flush=True)

print()
print("[FINAL HYPOTHESIS CLASSIFICATION]", flush=True)
if count['cnt'] == 0 and count_sig['cnt'] > 0:
    print("Status: E-PRIMARY_EVENT_NOT_PERSISTED_DUE_TO_DUPLICATE_OR_CONSTRAINT")
    print("Root Cause: INSERT OR IGNORE clause ignored the INSERT (event_id likely pre-existed)")
    print("           OR a constraint violation caused silent failure")
    print("Result: event_signatures written, events NOT written")
elif count['cnt'] > 0:
    print("Status: E-PRIMARY_EVENT_EXISTS_BUT_NOT_FOUND_IN_READ_BACK")
    print("Root Cause: Query or transaction isolation issue")
else:
    print("Status: E-UNKNOWN")

con.close()
