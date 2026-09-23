import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from phi_os import event_gate

# Monkey-patch _write to see what columns are being written
original_write = event_gate._write

def traced_write(payload: dict, conn=None):
    print("[TRACE] _write() payload:")
    print(f"  'event_source' in payload: {'event_source' in payload}")
    print(f"  payload.get('event_source'): {payload.get('event_source')}")
    print()

    # Recreate the row dict to see what's being written
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
        'channel_type':    'gate',
        'lifecycle_phase': 'in_operation',
        'risk_level':      'normal',
        'request_id':      payload.get('request_id'),
    }

    # Convert empty strings to None
    row = {k: (v if v != '' else None) for k, v in row.items()}

    print("[TRACE] _write() row dict:")
    for k, v in sorted(row.items()):
        if v is not None:
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: None")
    print()

    # Check if _source is None
    if row['_source'] is None:
        print("[TRACE] ✗ WARNING: _source is None (will violate NOT NULL constraint)")
    else:
        print(f"[TRACE] ✓ _source is '{row['_source']}'")

    return original_write(payload, conn)

event_gate._write = traced_write

from phi_os.event_gate import process_event

gate_payload = {
    "who_actor": "Claude-sonnet-5",
    "who_role": "governance",
    "who_session": "SESSION_20260920_000003",
    "what_type": "governance_block",
    "what_title": "[GOVERNANCE_BLOCK] column trace test",
    "where_path": "test.py",
    "where_component": "test",
    "why_purpose": "column trace test for governance_block",
    "how_trigger": "step5e_test",
    "after_state": "test state",
    "description": "test description",
}

print("=" * 70)
print("STEP 5E — COLUMN TRACE")
print("=" * 70)
print()

result = process_event(gate_payload, event_source="test:step5e")
print()
print(f"Result: {result}")
