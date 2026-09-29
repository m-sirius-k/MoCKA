#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — DETAILED EVENT STORE READ-BACK
Search events table for request_id, decision_id, event_id
"""

import sqlite3
import json

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
REQUEST_ID = "f63ae36f-06eb-4663-8dc5-b43de2c94ec1"
DECISION_ID = "DC_20260929_P5_HAB_JARVIS_001"
EVENT_ID = "E20260929_54766916458a0"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("[PHASE 5.0 DETAILED EVENT STORE READ-BACK]", flush=True)
print()

# Query events table structure
print("[EVENTS TABLE STRUCTURE]", flush=True)
cols = [x[1] for x in con.execute("PRAGMA table_info([events])")]
print(f"Columns: {cols}", flush=True)
print()

# Search by event_id (most specific)
print("[SEARCH BY EVENT_ID]", flush=True)
rows = con.execute("SELECT * FROM events WHERE event_id = ?", (EVENT_ID,)).fetchall()
if rows:
    print(f"Found {len(rows)} record(s)", flush=True)
    for row in rows:
        d = dict(row)
        print(f"  event_id: {d.get('event_id')}", flush=True)
        print(f"  request_id: {d.get('request_id')}", flush=True)
        print(f"  decision_id: {d.get('decision_id')}", flush=True)
        print(f"  timestamp: {d.get('when_ts') or d.get('timestamp')}", flush=True)
        print(f"  what_type: {d.get('what_type')}", flush=True)
        print(f"  who_actor: {d.get('who_actor')}", flush=True)

        # Check for payload/data field
        if "payload" in d:
            try:
                payload = json.loads(d["payload"]) if isinstance(d["payload"], str) else d["payload"]
                print(f"  payload_keys: {list(payload.keys()) if isinstance(payload, dict) else 'not a dict'}", flush=True)
            except:
                pass
else:
    print("Not found by event_id", flush=True)

print()

# Search by request_id
print("[SEARCH BY REQUEST_ID]", flush=True)
rows = con.execute("SELECT * FROM events WHERE request_id = ? LIMIT 5", (REQUEST_ID,)).fetchall()
if rows:
    print(f"Found {len(rows)} record(s)", flush=True)
    for row in rows:
        d = dict(row)
        print(f"  event_id: {d.get('event_id')}", flush=True)
        print(f"  request_id: {d.get('request_id')}", flush=True)
        print(f"  decision_id: {d.get('decision_id')}", flush=True)
        print(f"  what_type: {d.get('what_type')}", flush=True)
else:
    print("Not found by request_id", flush=True)

print()

# Search by decision_id
print("[SEARCH BY DECISION_ID]", flush=True)
rows = con.execute("SELECT * FROM events WHERE decision_id = ? LIMIT 5", (DECISION_ID,)).fetchall()
if rows:
    print(f"Found {len(rows)} record(s)", flush=True)
    for row in rows:
        d = dict(row)
        print(f"  event_id: {d.get('event_id')}", flush=True)
        print(f"  request_id: {d.get('request_id')}", flush=True)
        print(f"  decision_id: {d.get('decision_id')}", flush=True)
        print(f"  what_type: {d.get('what_type')}", flush=True)
else:
    print("Not found by decision_id", flush=True)

print()

# Search in event_signatures table for event_id
print("[EVENT_SIGNATURES TABLE SEARCH]", flush=True)
rows = con.execute("SELECT * FROM event_signatures WHERE event_id = ?", (EVENT_ID,)).fetchall()
if rows:
    print(f"Found {len(rows)} record(s)", flush=True)
    for row in rows:
        d = dict(row)
        for key in d.keys():
            print(f"  {key}: {d[key]}", flush=True)
else:
    print("Not found in event_signatures", flush=True)

print()
print("[FINAL VERIFICATION]", flush=True)

# Count events with any of our identifiers
event_count = con.execute("SELECT COUNT(*) as cnt FROM events WHERE event_id = ? OR request_id = ? OR decision_id = ?",
                         (EVENT_ID, REQUEST_ID, DECISION_ID)).fetchone()
print(f"Total events matching criteria: {event_count['cnt']}", flush=True)

con.close()
