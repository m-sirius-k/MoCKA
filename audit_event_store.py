#!/usr/bin/env python3
import sqlite3
import json

db = r'C:\Users\sirok\MoCKA\data\mocka_events.db'

try:
    con = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row

    print('=== TABLES ===')
    for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        print(r[0])

    print('\n=== SCHEMA COLUMNS ===')

    for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        table = r[0]
        try:
            cols = [x[1] for x in con.execute(f'PRAGMA table_info([{table}])')]
            print(f'{table}: {cols}')
        except Exception as e:
            print(f'{table} ERROR: {e}')

    print('\n=== TARGET SEARCH ===')

    targets = [
        'E20260929_7250201586747',
        '57531570-3b8f-4071-9a96-1f42af81cdfe'
    ]

    found_count = 0

    for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        table = r[0]
        cols = [x[1] for x in con.execute(f'PRAGMA table_info([{table}])')]
        textcols = [c for c in cols if c.lower() in (
            'event_id','request_id','decision_id','payload',
            'event','data','metadata','raw','content'
        )]

        if not textcols:
            continue

        for col in textcols:
            for target in targets:
                try:
                    q = f'SELECT * FROM [{table}] WHERE CAST([{col}] AS TEXT) LIKE ? LIMIT 20'
                    rows = con.execute(q, ('%' + target + '%',)).fetchall()
                    for row in rows:
                        found_count += 1
                        print(f'\nFOUND: TABLE={table} COLUMN={col} TARGET={target}')
                        d = dict(row)
                        for k, v in d.items():
                            print(f'  {k}: {v}')
                except Exception as e:
                    pass

    if found_count == 0:
        print('\nRESULT: NO MATCHES FOUND')
    else:
        print(f'\nTOTAL MATCHES: {found_count}')

    con.close()
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
