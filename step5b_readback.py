import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

print("=" * 70)
print("STEP 5B — READ-BACK VERIFICATION")
print("=" * 70)
print()

DB_PATH = str(Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db"))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Query for the event we just created
event_id = "E20260920_75513442107d2"

print(f"Searching for event_id: {event_id}")
print()

cursor = conn.execute(
    "SELECT * FROM events WHERE event_id = ?",
    (event_id,)
)

row = cursor.fetchone()

if row:
    print("✓ EVENT FOUND IN DATABASE")
    print()
    print("Event details:")
    print(f"  event_id: {row['event_id']}")
    print(f"  when_ts: {row['when_ts']}")
    print(f"  who_actor: {row['who_actor']}")
    print(f"  what_type: {row['what_type']}")
    print(f"  where_component: {row['where_component']}")
    print(f"  where_path: {row['where_path']}")
    print(f"  why_purpose: {row['why_purpose']}")
    print(f"  how_trigger: {row['how_trigger']}")
    print(f"  after_state: {row['after_state']}")
    print(f"  title: {row['title']}")
    print(f"  short_summary: {row['short_summary']}")
    print()

    # Verify what_type is governance_block
    if row['what_type'] == 'governance_block':
        print("✓ VERIFIED: what_type='governance_block' persisted correctly")
        readback_pass = True
    else:
        print(f"✗ MISMATCH: what_type is '{row['what_type']}', not 'governance_block'")
        readback_pass = False
else:
    print("✗ EVENT NOT FOUND")
    print()
    print("Searching for ANY governance_block events:")
    cursor2 = conn.execute(
        "SELECT event_id, what_type, title FROM events WHERE what_type = 'governance_block' LIMIT 5"
    )
    rows = cursor2.fetchall()
    if rows:
        for r in rows:
            print(f"  - {r['event_id']}: {r['what_type']} - {r['title']}")
    else:
        print("  (None found)")
    readback_pass = False

conn.close()

print()
print("=" * 70)
print("STEP 5B RESULT")
print("=" * 70)
if readback_pass:
    print("✓ READ-BACK: PASS")
    print("  governance_block event persisted and readable")
else:
    print("✗ READ-BACK: FAIL")
