"""
claude_sessions.csv → mocka_events.db(claude_sessionsテーブル) 移行スクリプト
実行: python migrate_sessions.py
"""
import sqlite3, csv
from pathlib import Path

DB_PATH  = Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db")
CSV_PATH = Path(r"C:\Users\sirok\MoCKA\data\claude_sessions.csv")

con = sqlite3.connect(str(DB_PATH))
con.execute("""CREATE TABLE IF NOT EXISTS claude_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    tool TEXT,
    args TEXT,
    result_summary TEXT
)""")
con.commit()

# 既存件数確認
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM claude_sessions")
existing = cur.fetchone()[0]
print(f"既存DB件数: {existing}")

if not CSV_PATH.exists():
    print(f"CSV未発見: {CSV_PATH}")
    con.close()
    exit(1)

with open(CSV_PATH, 'r', encoding='utf-8', errors='replace', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"CSV件数: {len(rows)}")

if existing >= len(rows):
    print("既に移行済み。スキップ。")
    con.close()
    exit(0)

inserted = 0
for row in rows:
    try:
        con.execute(
            "INSERT INTO claude_sessions (timestamp, tool, args, result_summary) VALUES (?,?,?,?)",
            (row.get('timestamp',''), row.get('tool',''),
             row.get('args','')[:500], row.get('result_summary','')[:200])
        )
        inserted += 1
    except Exception as e:
        print(f"  skip: {e}")

con.commit()
cur.execute("SELECT COUNT(*) FROM claude_sessions")
total = cur.fetchone()[0]
print(f"挿入: {inserted}件 → DB総件数: {total}件")
print("移行完了。")
con.close()
