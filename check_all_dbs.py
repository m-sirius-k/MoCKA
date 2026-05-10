import sqlite3
from pathlib import Path

dbs = [
    Path(r"C:\Users\sirok\MoCKA\data\events.db"),
    Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db"),
    Path(r"A:\MoCKA\data\events.db"),
]

for db in dbs:
    if not db.exists():
        print(f"[MISSING] {db}")
        continue
    size = db.stat().st_size
    if size == 0:
        print(f"[EMPTY]   {db} (0 bytes)")
        continue

    conn = sqlite3.connect(db)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n[DB] {db} ({size:,} bytes)")
    for t in tables:
        name = t[0]
        count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info([{name}])").fetchall()]
        print(f"  [{name}] {count}件 | cols={cols[:5]}")
        # user_voice / kimura発言を探す
        if 'what_type' in cols:
            types = conn.execute(f"SELECT what_type, COUNT(*) FROM [{name}] GROUP BY what_type ORDER BY 2 DESC LIMIT 5").fetchall()
            print(f"    top types: {types}")
        # サンプル（日本語正常データ）
        if 'title' in cols:
            sample = conn.execute(f"SELECT title FROM [{name}] WHERE title IS NOT NULL AND length(title) > 10 LIMIT 3").fetchall()
            for s in sample:
                t2 = s[0] or ""
                # 半角カナチェック
                hk = sum(1 for c in t2 if 0xFF61 <= ord(c) <= 0xFF9F)
                if hk == 0:
                    print(f"    正常サンプル: {t2[:60]}")
    conn.close()
