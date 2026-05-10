import sqlite3
from pathlib import Path

db = Path(r'C:\Users\sirok\MoCKA\data\events.db')
conn = sqlite3.connect(db)
rows = conn.execute("""
    SELECT title FROM events 
    WHERE what_type IN ('save','collaboration','share','record')
    LIMIT 50
""").fetchall()
conn.close()

targets = [
    "MoCKA 隲匁枚謠仙",
    "MoCKA 髫ｲ蛹",
    "MoCKA Orchestra",
    "MoCKA縺ｯ",
    "recurrence_registry隱",
    "GPT辟｡譁",
    "Firefox Chrome",
    "OAuth繝ｪ",
    "Git繝ｪ",
]

print("=== 文字化け行の実際のUnicodeコードポイント ===")
for row in rows:
    t = (row[0] or "")
    if not t: continue
    # 非ASCII文字を全部調べる
    non_ascii = [(c, hex(ord(c))) for c in t[:50] if ord(c) > 127]
    if non_ascii:
        ranges = set(hex(ord(c) >> 8) for c,_ in non_ascii)
        print(f"Text: {t[:50]!r}")
        print(f"  非ASCII範囲: {ranges}")
        print(f"  サンプル文字: {non_ascii[:5]}")
        print()
