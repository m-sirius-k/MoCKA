#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = 'data/mocka_events.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Most recent governance_block event
cursor.execute('''
    SELECT event_id, what_type, _source, when_ts, request_id
    FROM events
    WHERE what_type = 'governance_block'
    ORDER BY when_ts DESC
    LIMIT 3
''')

rows = cursor.fetchall()
conn.close()

print('=== EVENT READ-BACK: Last 3 governance_block events ===')
print()
for event_id, what_type, _source, when_ts, request_id in rows:
    print(f'Event ID:     {event_id}')
    print(f'what_type:    {what_type}')
    print(f'_source:      {_source}')
    print(f'when_ts:      {when_ts}')
    print(f'request_id:   {request_id}')
    print()

print('=== VERIFICATION SUMMARY ===')
if rows:
    latest = rows[0]
    event_id, what_type, _source, when_ts, request_id = latest
    print(f'✓ Event read-back: SUCCESS (event_id={event_id})')
    print(f'✓ _source value:   {repr(_source)} (expected: "live")')
    print(f'✓ what_type:       {repr(what_type)} (expected: "governance_block")')

    checks = []
    if _source == 'live':
        checks.append(('_source value', True))
        print('  → _source="live" is in ALLOWED_SOURCE_VALUES: PASS')
    else:
        checks.append(('_source value', False))
        print(f'  → _source="{_source}" is NOT "live": FAIL')

    if what_type == 'governance_block':
        checks.append(('what_type value', True))
        print('  → what_type="governance_block": PASS')
    else:
        checks.append(('what_type value', False))
        print(f'  → what_type="{what_type}" is NOT "governance_block": FAIL')

    all_pass = all(result for _, result in checks)
    print()
    print(f'Overall read-back verification: {"PASS" if all_pass else "FAIL"}')
else:
    print('✗ No governance_block events found in DB')
