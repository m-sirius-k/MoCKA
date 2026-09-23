import sqlite3
from pathlib import Path

db_path = Path('data/mocka_events.db')
if db_path.exists():
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row

    try:
        rows = con.execute('SELECT * FROM decision_id_counters ORDER BY date DESC LIMIT 10').fetchall()
        print('COUNTER TABLE:')
        for row in rows:
            print(f"  {row['date']}: counter={row['counter']}")
    except Exception as e:
        print(f'Counter table error: {e}')

    con.close()
else:
    print('DB not found')
