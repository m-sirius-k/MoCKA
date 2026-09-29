import sqlite3

p = r'C:\Users\sirok\MoCKA\data\mocka_events.db'
c = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
q = c.cursor()

print('=== EVENT_BUS ===')
event_bus_result = q.execute("SELECT * FROM event_bus WHERE event_id='E20260929_54766916458a0'").fetchall()
if event_bus_result:
    for row in event_bus_result:
        print(row)
else:
    print('NOT FOUND')

print('\n=== EVENT_SIGNATURES ===')
sig_result = q.execute("SELECT * FROM event_signatures WHERE event_id='E20260929_54766916458a0'").fetchall()
if sig_result:
    for row in sig_result:
        print(row)
else:
    print('NOT FOUND')

print('\n=== TABLE SCHEMAS ===')
schemas = q.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('event_bus', 'event_signatures')").fetchall()
for name, sql in schemas:
    print(f'\n{name}:')
    print(sql if sql else '(no CREATE statement)')

c.close()
