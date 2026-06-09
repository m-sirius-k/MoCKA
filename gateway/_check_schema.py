import sqlite3
conn = sqlite3.connect(r'C:\Users\sirok\MoCKA\data\mocka_events.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in cur.fetchall():
    cur.execute(f"PRAGMA table_info({t[0]})")
    print(f"\n=== {t[0]} ===")
    for c in cur.fetchall():
        print(f"  {c[1]} {c[2]}")
conn.close()
