import sqlite3
from datetime import datetime, timezone

print("=" * 70)
print("PING 1 — EXACT SQLITE CONSTRAINT ERROR")
print("=" * 70)
print()

# Generate payload identical to process_event() call
payload = {
    "who_actor": "Claude-sonnet-5",
    "who_role": "governance",
    "who_session": "SESSION_20260920_150000",
    "what_type": "governance_block",
    "what_title": "[GOVERNANCE_BLOCK] PING 1 error capture",
    "where_path": "governance_pipeline.py",
    "where_component": "ba04_execution_gate",
    "why_purpose": "Authority Decision Enforcement (BA-04)",
    "how_trigger": "before_tool() BLOCK",
    "after_state": "Execution BLOCKED",
    "description": "Test error capture",
    "event_source": "ping1:test",
}

# Build row dict exactly as _write() does
row = {
    'event_id':        payload.get('event_id', '') or f"E{datetime.now().strftime('%Y%m%d_%H%M%S')}_test001",
    'when_ts':         payload.get('when_ts') or datetime.now(timezone.utc).isoformat(),
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
    'free_note':       '',
    'channel_type':    'gate',
    'lifecycle_phase': 'in_operation',
    'risk_level':      'normal',
    'request_id':      payload.get('request_id'),
}

# Convert empty strings to None
row = {k: (v if v != '' else None) for k, v in row.items()}

print("Payload (governance_block):")
for k, v in sorted(row.items()):
    if v is not None:
        print(f"  {k:<20}: {str(v)[:60]}")
print()

# Try INSERT with normal SQL (not INSERT OR IGNORE)
conn = sqlite3.connect('data/mocka_events.db')

try:
    cols = list(row.keys())
    placeholders = ','.join('?' * len(cols))
    vals = [row[c] for c in cols]

    sql = f'INSERT INTO events ({",".join(cols)}) VALUES ({placeholders})'

    print("Attempting normal INSERT (not INSERT OR IGNORE)...")
    print()

    cursor = conn.execute(sql, vals)
    conn.commit()
    print("✓ INSERT succeeded")
    print(f"  Rowcount: {cursor.rowcount}")

except sqlite3.IntegrityError as e:
    print("✗ sqlite3.IntegrityError raised")
    print(f"  Error: {e}")
    print(f"  Type: {type(e).__name__}")
    print()

    # Parse the error to identify constraint
    error_str = str(e)
    if 'UNIQUE' in error_str:
        print("  Constraint type: UNIQUE")
    elif 'PRIMARY' in error_str:
        print("  Constraint type: PRIMARY KEY")
    elif 'FOREIGN' in error_str:
        print("  Constraint type: FOREIGN KEY")
    elif 'NOT NULL' in error_str:
        print("  Constraint type: NOT NULL")
    else:
        print("  Constraint type: OTHER")

    # Extract which column
    print()
    print("Analysis:")
    print("  This error means the INSERT is being rejected due to a constraint")
    print("  INSERT OR IGNORE silently skips this error")
    print("  Causing process_event() to return status='ok' but not persist")

except Exception as e:
    print(f"✗ Unexpected exception: {type(e).__name__}: {e}")

finally:
    conn.close()
