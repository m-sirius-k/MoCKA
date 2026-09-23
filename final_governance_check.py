import sqlite3

conn = sqlite3.connect('data/mocka_events.db')
cursor = conn.cursor()

# Count ALL governance_block events
cursor.execute("SELECT COUNT(*) FROM events WHERE what_type = 'governance_block'")
count = cursor.fetchone()[0]
print(f'Total governance_block events in DB: {count}')

# List them
cursor.execute("SELECT event_id, when_ts, title FROM events WHERE what_type = 'governance_block' ORDER BY when_ts DESC LIMIT 5")
rows = cursor.fetchall()
if rows:
    print()
    print('governance_block events:')
    for row in rows:
        print(f'  {row[0]}: {row[1][:19]} - {row[2][:60]}')
else:
    print()
    print('No governance_block events in database')

conn.close()
