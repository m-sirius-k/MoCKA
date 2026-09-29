#!/usr/bin/env python3
import sqlite3
import json

db = r'C:\Users\sirok\MoCKA\data\mocka_events.db'

try:
    con = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row

    print('=== SEARCH 1: events TABLE — event_id exact match ===')

    event_id = 'E20260929_7250201586747'

    q = 'SELECT * FROM events WHERE event_id = ?'
    rows = con.execute(q, (event_id,)).fetchall()

    if rows:
        for row in rows:
            print(f'FOUND in events table:')
            d = dict(row)
            for k, v in sorted(d.items()):
                print(f'  {k}: {v}')
    else:
        print(f'NOT FOUND in events table')

    print('\n=== SEARCH 2: request_id exact match ===')

    request_id = '57531570-3b8f-4071-9a96-1f42af81cdfe'

    q = 'SELECT * FROM events WHERE request_id = ?'
    rows = con.execute(q, (request_id,)).fetchall()

    if rows:
        print(f'FOUND {len(rows)} records with request_id={request_id}:')
        for row in rows:
            d = dict(row)
            print(f'  event_id: {d.get("event_id")}')
            print(f'  request_id: {d.get("request_id")}')
            print(f'  decision_id: {d.get("decision_id")}')
            print(f'  vendor: {d.get("vendor")}')
            print(f'  model: {d.get("model")}')
            print(f'  runtime: {d.get("runtime")}')
            print(f'  when_ts: {d.get("when_ts")}')
            print()
    else:
        print(f'NOT FOUND in events table with request_id={request_id}')

    print('\n=== SEARCH 3: Recent events with vendor/model (multi-AI indicator) ===')

    q = 'SELECT event_id, when_ts, request_id, vendor, model, runtime FROM events WHERE vendor IS NOT NULL ORDER BY when_ts DESC LIMIT 10'
    rows = con.execute(q).fetchall()

    if rows:
        print(f'Recent events with vendor/model:')
        for row in rows:
            d = dict(row)
            print(f'  {d.get("event_id")} | {d.get("when_ts")} | {d.get("vendor")} | {d.get("model")} | {d.get("request_id")}')

    print('\n=== SEARCH 4: Events by date (2026-09-29) ===')

    q = 'SELECT event_id, when_ts, request_id, what_type, title FROM events WHERE when_ts LIKE ? ORDER BY when_ts DESC LIMIT 20'
    rows = con.execute(q, ('2026-09-29%',)).fetchall()

    if rows:
        print(f'Events on 2026-09-29:')
        for row in rows:
            d = dict(row)
            print(f'  {d.get("event_id")} | {d.get("when_ts")} | type={d.get("what_type")} | {d.get("title")}')

    print('\n=== SEARCH 5: human_gate_events with request_id ===')

    q = 'SELECT * FROM human_gate_events WHERE request_id = ?'
    rows = con.execute(q, (request_id,)).fetchall()

    if rows:
        print(f'FOUND in human_gate_events:')
        for row in rows:
            d = dict(row)
            for k, v in sorted(d.items()):
                print(f'  {k}: {v}')
    else:
        print(f'NOT FOUND in human_gate_events')

    con.close()
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
