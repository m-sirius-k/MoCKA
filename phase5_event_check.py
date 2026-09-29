#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check event in events table
"""

import sqlite3

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
EVENT_ID = "E20260929_54766916458a0"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("[CHECKING EVENT IN EVENTS TABLE]", flush=True)

rows = con.execute("SELECT * FROM events WHERE event_id = ?", (EVENT_ID,)).fetchall()

if rows:
    print(f"Found {len(rows)} record(s)", flush=True)
    for row in rows:
        d = dict(row)
        print()
        print(f"Event ID: {d.get('event_id')}", flush=True)
        print(f"When: {d.get('when_ts')}", flush=True)
        print(f"What: {d.get('what_type')}", flush=True)
        print(f"Who: {d.get('who_actor')}", flush=True)
        print(f"Request ID: {d.get('request_id')}", flush=True)
        print(f"Title: {d.get('title')}", flush=True)
        print(f"Vendor: {d.get('vendor')}", flush=True)
        print(f"Model: {d.get('model')}", flush=True)
        print(f"Free Note: {str(d.get('free_note'))[:200]}", flush=True)
else:
    print("Event not found in events table", flush=True)
    print()

    print("[CHECKING RECENT EVENTS FOR COMPARISON]", flush=True)
    recent = con.execute("SELECT event_id, when_ts, what_type, who_actor, request_id FROM events ORDER BY rowid DESC LIMIT 15").fetchall()
    print(f"Recent {len(recent)} events:", flush=True)
    for row in recent:
        d = dict(row)
        print(f"  {d.get('event_id')}: {d.get('what_type')} | request_id={d.get('request_id')}", flush=True)

con.close()
