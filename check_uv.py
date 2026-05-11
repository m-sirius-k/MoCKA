import sqlite3
from pathlib import Path

conn = sqlite3.connect(r'C:\Users\sirok\MoCKA\data\mocka_events.db')
rows = conn.execute(
    "SELECT event_id, when_ts, free_note FROM events WHERE what_type='user_voice' ORDER BY when_ts DESC LIMIT 5"
).fetchall()
if rows:
    for r in rows:
        print(r[0], r[1], str(r[2])[:80])
else:
    print("user_voiceレコードなし")
conn.close()
