#!/usr/bin/env python3
"""Audit decision_id_counters table state"""

import sqlite3
import datetime
from pathlib import Path

db_path = Path('data/mocka_events.db')
con = sqlite3.connect(str(db_path), timeout=10.0)

# Check if table exists
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
table_names = [t[0] for t in tables]

print('Tables in database:')
for table in sorted(table_names):
    print(f'  - {table}')

# Query decision_id_counters
if 'decision_id_counters' in table_names:
    print(f'\nContents of decision_id_counters:')
    rows = con.execute('SELECT date, counter FROM decision_id_counters ORDER BY date').fetchall()
    print(f'Total entries: {len(rows)}')

    for row in rows[-10:]:  # Last 10 days
        print(f'  {row[0]}: counter={row[1]}')

    today = datetime.date.today().strftime('%Y%m%d')
    counter = con.execute('SELECT counter FROM decision_id_counters WHERE date = ?', (today,)).fetchone()
    if counter:
        print(f'\n*** TODAY ({today}): counter = {counter[0]} ***')
    else:
        print(f'\n*** No entry for today ({today}) ***')
else:
    print('decision_id_counters table not found')

con.close()
