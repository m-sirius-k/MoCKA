import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/mocka_events.db')
conn.row_factory = sqlite3.Row

# Get recent governance events
cursor = conn.execute('''
  SELECT event_id, when_ts, what_type, title
  FROM events
  WHERE what_type = 'governance_block'
     OR title LIKE '%GOVERNANCE%'
  ORDER BY when_ts DESC
  LIMIT 10
''')

rows = cursor.fetchall()
print(f'Found {len(rows)} governance_block events:')
for row in rows:
    print(f"  {row['event_id']}: {row['what_type']:<20} {row['title'][:60]}")

# Also check most recent events
print()
print('Most recent events (any type):')
cursor2 = conn.execute('''
  SELECT event_id, when_ts, what_type, title
  FROM events
  ORDER BY when_ts DESC
  LIMIT 5
''')

rows2 = cursor2.fetchall()
for row in rows2:
    print(f"  {row['event_id']}: {row['what_type']:<20} {row['title'][:60]}")

conn.close()
