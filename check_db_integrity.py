import sqlite3

conn = sqlite3.connect('data/mocka_events.db')
cursor = conn.cursor()

# Check if events table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
if cursor.fetchone():
    print('✓ events table exists')

    # Get table info
    cursor.execute('PRAGMA table_info(events)')
    cols = cursor.fetchall()
    print(f'✓ Table has {len(cols)} columns')

    # Check record count
    cursor.execute('SELECT COUNT(*) FROM events')
    count = cursor.fetchone()[0]
    print(f'✓ Total records in events: {count}')

    # Check if we can write
    try:
        cursor.execute("INSERT INTO events (event_id, when_ts, what_type) VALUES ('TEST_ID_12345', '2026-09-20T00:00:00Z', 'test')")
        conn.commit()
        print('✓ Can write to table')

        # Verify write
        cursor.execute("SELECT COUNT(*) FROM events WHERE event_id = 'TEST_ID_12345'")
        if cursor.fetchone()[0] > 0:
            print('✓ Verify write succeeded')
        else:
            print('✗ Write succeeded but record not found')

        # Clean up test
        cursor.execute("DELETE FROM events WHERE event_id = 'TEST_ID_12345'")
        conn.commit()
        print('✓ Can delete from table')
    except Exception as e:
        print(f'✗ Write error: {e}')
else:
    print('✗ events table does not exist')

conn.close()
