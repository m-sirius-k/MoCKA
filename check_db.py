import sqlite3
from pathlib import Path

db = Path(r'C:\Users\sirok\MoCKA\mocka_events.db')
print('DB exists:', db.exists())
print('DB size:', db.stat().st_size if db.exists() else 'N/A')

conn = sqlite3.connect(db)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', tables)

for t in tables:
    name = t[0]
    count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info([{name}])").fetchall()]
    print(f"  {name}: {count}件 | cols={cols[:6]}")

conn.close()
