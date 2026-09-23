import sqlite3
from datetime import datetime

print("=" * 70)
print("STEP 4 — READ-BACK VERIFICATION")
print("=" * 70)
print()

DB_PATH = "data/mocka_events.db"
event_id = "E20260920_122687400cbb5"
req_id = "req_online_e2e_001"

print(f"Searching for event_id: {event_id}")
print(f"Also searching for req_id: {req_id}")
print()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Query by event_id
print("A. Query by event_id:")
cursor = conn.execute(
    "SELECT * FROM events WHERE event_id = ?",
    (event_id,)
)
row = cursor.fetchone()

if row:
    print(f"✓ FOUND: {event_id}")
    print()
    print("Verification:")
    print(f"  1. what_type: {row['what_type']}")
    if row['what_type'] == 'governance_block':
        print("     ✓ CORRECT (governance_block)")
    else:
        print(f"     ✗ WRONG (expected governance_block, got {row['what_type']})")

    print(f"  2. request_id: {row['request_id']}")
    if row['request_id'] == req_id:
        print("     ✓ CORRECT (matches request)")
    else:
        print(f"     ✗ WRONG (expected {req_id})")

    print(f"  3. title: {row['title']}")
    print(f"  4. short_summary: {row['short_summary'][:100] if row['short_summary'] else 'None'}")
    print(f"  5. after_state: {row['after_state']}")
    print(f"  6. who_actor: {row['who_actor']}")
    print(f"  7. where_component: {row['where_component']}")
    print(f"  8. _source: {row['_source']}")
    print(f"  9. when_ts: {row['when_ts']}")

    readback_pass = (row['what_type'] == 'governance_block' and row['request_id'] == req_id)
else:
    print(f"✗ NOT FOUND: {event_id}")
    readback_pass = False

print()

# Query by request_id
print("B. Query by request_id:")
cursor2 = conn.execute(
    "SELECT event_id, what_type, title FROM events WHERE request_id = ?",
    (req_id,)
)
rows = cursor2.fetchall()

if rows:
    print(f"✓ Found {len(rows)} event(s) with request_id={req_id}")
    for r in rows:
        print(f"  - {r['event_id']}: {r['what_type']} - {r['title'][:50]}")
else:
    print(f"✗ No events with request_id={req_id}")

conn.close()

print()
print("=" * 70)
print("STEP 4 RESULT")
print("=" * 70)
if readback_pass:
    print("✓ READ-BACK: PASS")
    print("  governance_block event persisted and readable")
    print("  Request ID matches")
else:
    print("✗ READ-BACK: FAIL or PARTIAL")
    if row:
        print("  Event exists but details don't match")
    else:
        print("  Event not found in database")
