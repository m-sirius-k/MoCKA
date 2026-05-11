import sqlite3

db = r'C:\Users\sirok\MoCKA\data\mocka_events.db'
conn = sqlite3.connect(db)

keep = conn.execute("SELECT COUNT(*) FROM guidelines_reviewed WHERE verdict IN ('keep','edit')").fetchone()[0]
skip = conn.execute("SELECT COUNT(*) FROM guidelines_reviewed WHERE verdict='skip'").fetchone()[0]
cats = conn.execute("SELECT category, COUNT(*) FROM guidelines_reviewed WHERE verdict IN ('keep','edit') GROUP BY category ORDER BY COUNT(*) DESC").fetchall()

conn.close()

print(f'採用: {keep}件')
print(f'除外: {skip}件')
print('--- カテゴリ別 ---')
for cat, cnt in cats:
    print(f'  {cat}: {cnt}件')
