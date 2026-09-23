import sqlite3

db = sqlite3.connect('data/mocka_events.db')
cursor = db.cursor()

print('=== EVENTS TABLE SCHEMA ===')
cursor.execute("PRAGMA table_info(events)")
for col_id, col_name, col_type, not_null, default, pk in cursor.fetchall():
    print(f'{col_id}: {col_name} ({col_type})')

db.close()
