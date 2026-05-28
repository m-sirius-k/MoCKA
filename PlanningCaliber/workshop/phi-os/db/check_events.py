import sqlite3
DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT DISTINCT what_type FROM events ORDER BY what_type")
print("what_type values:", [r[0] for r in c.fetchall()])
c.execute("SELECT event_id, what_type, title, when_ts FROM events ORDER BY when_ts DESC LIMIT 5")
for r in c.fetchall(): print(r)
conn.close()
