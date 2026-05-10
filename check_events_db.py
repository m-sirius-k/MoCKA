import sqlite3
from pathlib import Path

db = Path(r'C:\Users\sirok\MoCKA\data\events.db')
conn = sqlite3.connect(db)

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])

for t in tables:
    name = t[0]
    count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info([{name}])").fetchall()]
    print(f"\n[{name}] {count}件")
    print(f"  cols: {cols}")
    # サンプル1件
    row = conn.execute(f"SELECT * FROM [{name}] LIMIT 1").fetchone()
    if row:
        for c, v in zip(cols, row):
            print(f"  {c}: {str(v)[:80]}")

conn.close()
