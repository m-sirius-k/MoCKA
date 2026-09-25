import sqlite3
from pathlib import Path
import os

def _get_repository_root():
    """Auto-detect repository root by looking for .git directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent

_MOCKA_ROOT_ENV = os.environ.get("MOCKA_ROOT")
BASE = Path(_MOCKA_ROOT_ENV) if _MOCKA_ROOT_ENV else _get_repository_root()

db = BASE / 'data' / 'events.db'
conn = sqlite3.connect(db)
# 文字化け行のサンプル取得
rows = conn.execute("""
    SELECT title FROM events 
    WHERE what_type IN ('save','collaboration','share')
    LIMIT 20
""").fetchall()
conn.close()

print("=== 文字化け文字のコードポイント調査 ===")
for row in rows:
    t = (row[0] or "")[:80]
    # 非ASCII・非日本語通常文字を探す
    suspicious = [(c, hex(ord(c))) for c in t 
                  if ord(c) > 127 and not '\u3000' <= c <= '\u9FFF'
                  and not '\uFF00' <= c <= '\uFFEF']
    if suspicious:
        print(f"Text: {t[:40]}")
        print(f"  怪しい文字: {suspicious[:8]}")
        print()
