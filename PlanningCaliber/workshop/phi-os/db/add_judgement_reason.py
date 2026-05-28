"""
add_judgement_reason.py
DNA_v3 Step2: mocka_events.db に judgement_reason テーブルを追加する。

実際のDBパス: C:\Users\sirok\MoCKA\data\mocka_events.db
仕様書記載パス: C:\Users\sirok\MoCKA\mocka_events.db  ← 0バイトの空ファイル
→ data/ サブディレクトリの方が正しい（30MB、8テーブル存在）
"""
import sqlite3
import os
import sys

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
SQL_PATH = os.path.join(os.path.dirname(__file__), "migration_v1.sql")

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(SQL_PATH, encoding="utf-8") as f:
        sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
        print("[OK] migration_v1.sql 実行完了")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] migration 失敗: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

def verify():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='judgement_reason'")
    assert c.fetchone(), "judgement_reason テーブルが存在しない"
    print("[PASS] judgement_reason テーブル存在確認")

    c.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='judgement_reason'")
    indexes = {r[0] for r in c.fetchall()}
    required = {"idx_jr_tags", "idx_jr_tension", "idx_jr_session", "idx_jr_event"}
    missing = required - indexes
    assert not missing, f"インデックス不足: {missing}"
    print("[PASS] インデックス全4件確認")

    conn.close()

if __name__ == "__main__":
    print(f"DB: {DB_PATH}")
    run_migration()
    verify()
    print("=== Step2 migration PASS ===")
