import sqlite3

conn = sqlite3.connect('data/mocka_events.db')
cursor = conn.cursor()

print('Table: events')
print()

# Check for UNIQUE constraints
print('UNIQUE constraints / indexes:')
cursor.execute("PRAGMA index_list(events)")
indexes = cursor.fetchall()
for idx in indexes:
    seq, name, unique, origin, partial = idx
    if unique:
        print(f'  {name} (unique={unique})')
        cursor.execute(f'PRAGMA index_info({name})')
        cols = cursor.fetchall()
        for col in cols:
            print(f'    - {col[2]}')

print()

# Check for PRIMARY KEY
print('PRIMARY KEY:')
cursor.execute('PRAGMA table_info(events)')
cols = cursor.fetchall()
for col in cols:
    col_id, name, type_, notnull, dflt_value, pk = col
    if pk:
        print(f'  {name}')

print()
print('Possible root cause of INSERT OR IGNORE failure:')
print('  - event_id might be a PRIMARY KEY')
print('  - Or there might be a UNIQUE constraint that we are violating')

conn.close()
