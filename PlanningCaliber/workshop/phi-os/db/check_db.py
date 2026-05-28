import sqlite3

DB_PATH = r"C:\Users\sirok\MoCKA\mocka_events.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)
conn.close()
