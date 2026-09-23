import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))

from phi_os import event_gate
from phi_os.gate_schema import ALLOWED_WHAT_TYPES

print("=" * 70)
print("STEP 5 — INSERT OR IGNORE TRACE")
print("=" * 70)
print()

# Monkey-patch _write to trace the actual SQL
original_write = event_gate._write

def traced_write(payload: dict, conn=None):
    print("[TRACE] _write() called")
    print(f"  payload event_source: {payload.get('event_source')}")
    print()

    # Recreate row dict exactly as _write does
    row = {
        'event_id':        payload.get('event_id', ''),
        'when_ts':         payload.get('when_ts') or payload.get('when', ''),
        'who_actor':       payload.get('who_actor', ''),
        'what_type':       payload.get('what_type', ''),
        'where_component': payload.get('where_component', ''),
        'where_path':      payload.get('where_path', ''),
        'why_purpose':     payload.get('why_purpose', ''),
        'how_trigger':     payload.get('how_trigger', ''),
        'before_state':    payload.get('before_state', ''),
        'after_state':     payload.get('after_state', ''),
        'title':           payload.get('what_title') or payload.get('title', ''),
        'short_summary':   payload.get('description') or payload.get('short_summary', ''),
        'session_id':      payload.get('who_session') or payload.get('session_id', ''),
        '_source':         payload.get('event_source', 'live'),
        'free_note': '',
        'channel_type':    'gate',
        'lifecycle_phase': 'in_operation',
        'risk_level':      'normal',
        'request_id':      payload.get('request_id'),
    }

    # Convert empty strings to None
    row = {k: (v if v != '' else None) for k, v in row.items()}

    # Get or create connection
    owns_conn = conn is None
    if owns_conn:
        conn = sqlite3.connect("data/mocka_events.db")

    try:
        # Build the INSERT statement exactly as _write does
        cols = list(row.keys())
        placeholders = ','.join('?' * len(cols))
        vals = [row[c] for c in cols]

        sql = f'INSERT OR IGNORE INTO events ({",".join(cols)}) VALUES ({placeholders})'

        print("[TRACE] Attempting INSERT OR IGNORE...")
        print(f"  SQL: {sql[:100]}...")
        print(f"  Columns: {len(cols)}")
        print(f"  Values: event_id={row['event_id']}, what_type={row['what_type']}, _source={row['_source']}")
        print()

        # Execute the INSERT
        cursor = conn.execute(sql, vals)

        # Check rowcount to see if INSERT actually happened
        print(f"  Rowcount after INSERT: {cursor.rowcount}")
        if cursor.rowcount == 0:
            print("  ✗ INSERT was ignored (constraint violation?)")
        elif cursor.rowcount == 1:
            print("  ✓ INSERT succeeded")
        print()

        # Now check if the record actually exists
        check_cursor = conn.execute(
            "SELECT COUNT(*) as cnt FROM events WHERE event_id = ?",
            (row['event_id'],)
        )
        count = check_cursor.fetchone()[0]
        print(f"  Verify: SELECT COUNT(*) WHERE event_id={row['event_id']} = {count}")

        if count == 0:
            print("  ✗ INSERT OR IGNORE silently skipped the insert")
        else:
            print("  ✓ Record exists after INSERT")

        # Don't call the rest of the original function (signature signing, etc)
        # Just verify the INSERT behavior

        if owns_conn:
            conn.commit()

    finally:
        if owns_conn:
            conn.close()

event_gate._write = traced_write

# Now test with process_event
from phi_os.event_gate import process_event

payload = {
    "who_actor": "test",
    "who_role": "governance",
    "who_session": "SESSION_20260920_130000",
    "what_type": "governance_block",
    "where_component": "test",
    "where_path": "/test",
    "why_purpose": "INSERT trace test",
    "how_trigger": "test",
    "after_state": "test",
}

print("Calling process_event()...")
result = process_event(payload, event_source="test:step5")
print(f"Result: {result}")
