import sqlite3
from datetime import datetime, timezone

print("=" * 70)
print("PING 3 — EVENT TYPE COMPARISON")
print("=" * 70)
print()

# Test multiple event types with CORRECT _source value
test_cases = [
    ("governance_block", "live"),      # What we're adding
    ("audit", "live"),                  # Existing type
    ("incident", "live"),               # Existing type
]

conn = sqlite3.connect('data/mocka_events.db')

for what_type, source_value in test_cases:
    print(f"Test: what_type='{what_type}', _source='{source_value}'")
    print("-" * 50)

    row = {
        'event_id':        f"E{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:13]}_{what_type}_t",
        'when_ts':         datetime.now(timezone.utc).isoformat(),
        'who_actor':       "test_actor",
        'what_type':       what_type,
        'where_component': "test_component",
        'where_path':      "/test/path",
        'why_purpose':     "test purpose",
        'how_trigger':     "test_trigger",
        'before_state':    None,
        'after_state':     "test_state",
        'title':           f"Test {what_type}",
        'short_summary':   "test",
        'session_id':      "SESSION_20260920_000000",
        '_source':         source_value,
        'free_note':       "",
        'channel_type':    'gate',
        'lifecycle_phase': 'in_operation',
        'risk_level':      'normal',
        'request_id':      None,
    }

    # Convert empty strings to None
    row = {k: (v if v != '' else None) for k, v in row.items()}

    try:
        cols = list(row.keys())
        placeholders = ','.join('?' * len(cols))
        vals = [row[c] for c in cols]

        sql = f'INSERT INTO events ({",".join(cols)}) VALUES ({placeholders})'

        cursor = conn.execute(sql, vals)
        conn.commit()
        print(f"✓ INSERT succeeded")
        print(f"  event_id: {row['event_id']}")

    except sqlite3.IntegrityError as e:
        print(f"✗ IntegrityError: {str(e)[:100]}")
    except Exception as e:
        print(f"✗ {type(e).__name__}: {e}")

    print()

conn.close()

print("=" * 70)
print("PING 3 CONCLUSION")
print("=" * 70)
print()
print("If all tests PASS with _source='live':")
print("  → The issue is the _source value, not governance_block itself")
print("  → governance_block type itself is working correctly")
print()
print("If all tests FAIL:")
print("  → Pre-existing bug affects all event types")
