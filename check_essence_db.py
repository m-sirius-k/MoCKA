import sqlite3, json
from pathlib import Path

# essence場所を探す
print("=== lever_essence.json 検索 ===")
for root in [Path(r"C:\Users\sirok\MoCKA"), Path(r"A:\MoCKA")]:
    if root.exists():
        for f in root.rglob("lever_essence.json"):
            print(f"  FOUND: {f}")
        for f in root.rglob("*essence*.json"):
            print(f"  essence系: {f}")

# DBのwhat_type / risk_level分布
print("\n=== events.db 分布 ===")
db = Path(r'C:\Users\sirok\MoCKA\data\events.db')
conn = sqlite3.connect(db)
print("what_type:")
for row in conn.execute("SELECT what_type, COUNT(*) c FROM events GROUP BY what_type ORDER BY c DESC").fetchall():
    print(f"  {row[0]}: {row[1]}件")
print("risk_level:")
for row in conn.execute("SELECT risk_level, COUNT(*) c FROM events GROUP BY risk_level ORDER BY c DESC").fetchall():
    print(f"  {row[0]}: {row[1]}件")
conn.close()
