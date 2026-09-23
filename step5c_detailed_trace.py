import sys
import json
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from phi_os.event_gate import process_event
from phi_os.gate_schema import ALLOWED_WHAT_TYPES

print("=" * 70)
print("STEP 5C — DETAILED TRACE")
print("=" * 70)
print()

# Verify schema
print("A. Schema verification:")
print(f"   'governance_block' in ALLOWED_WHAT_TYPES: {'governance_block' in ALLOWED_WHAT_TYPES}")
print()

# Create payload
gate_payload = {
    "who_actor": "Claude-sonnet-5",
    "who_role": "governance",
    "who_session": "SESSION_20260920_000001",
    "what_type": "governance_block",
    "what_title": "[GOVERNANCE_BLOCK] step5c test",
    "where_path": "test.py",
    "where_component": "test",
    "why_purpose": "detailed trace test for governance_block",
    "how_trigger": "step5c_test",
    "after_state": "test state",
    "description": "test description",
}

print("B. Calling process_event()...")

try:
    result = process_event(gate_payload, event_source="test:step5c")
    print(f"   Status: {result.get('status')}")
    print(f"   Event ID: {result.get('event_id')}")
    print(f"   Full result: {result}")
    event_id = result.get('event_id')
except Exception as e:
    print(f"   Exception: {type(e).__name__}: {e}")
    event_id = None

print()

if event_id:
    print("C. Attempting to read event from database...")

    conn = sqlite3.connect("data/mocka_events.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.execute(
        "SELECT event_id, what_type, title FROM events WHERE event_id = ?",
        (event_id,)
    )
    row = cursor.fetchone()

    if row:
        print(f"   ✓ FOUND: {row['event_id']} ({row['what_type']})")
        print(f"   Title: {row['title']}")
    else:
        print(f"   ✗ NOT FOUND: {event_id}")

        # Check if any event was created at all
        cursor2 = conn.execute(
            "SELECT COUNT(*) as cnt FROM events WHERE what_type = 'governance_block'"
        )
        count = cursor2.fetchone()['cnt']
        print(f"   Total governance_block events in DB: {count}")

    conn.close()
