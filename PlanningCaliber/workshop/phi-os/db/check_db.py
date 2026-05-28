import sqlite3

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)
for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    cols = [(r[1], r[2]) for r in c.fetchall()]
    c.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = c.fetchone()[0]
    print(f"  [{t}] rows={cnt} cols={cols}")
conn.close()
