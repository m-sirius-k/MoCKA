# -*- coding: utf-8 -*-
"""
structural/phi_dna_migrate.py — PHI Decision DNA β拡張マイグレーション（TODO_212）
judgement_reason テーブルに 6カラムを追加する。
冪等: 既にカラムが存在する場合はスキップする。
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db")

NEW_COLUMNS = [
    ("observation",    "TEXT", None, "何を観測したか（TICイベント・DOM変化等）"),
    ("interpretation", "TEXT", None, "どう解釈したか（構造タグとの照合結果）"),
    ("hypothesis",     "TEXT", None, "立てた仮説（β候補）"),
    ("beta_id",        "TEXT", None, "関連するβID（beta_registry.json のキー）"),
    ("opportunity",    "TEXT", None, "発見した機会（Opportunity Score）"),
    ("validated_at",   "TEXT", None, "後日検証した日時（ISO8601）"),
]

EXAMPLE_RECORD = {
    "event_id":      "E20260601_068",
    "session_date":  "2026-06-01",
    "decision":      "Relay content.js を修正した",
    "reason":        "LB_005 レースコンディションが確認されたため",
    "observation":   "Claude DOM構造が変化し、Relay セレクタが消失した",
    "interpretation":"非公式UI依存（ui_dependency）が顕在化。官式API移行が求められている",
    "hypothesis":    "MCP移行でこの問題は構造的に解決できる（β: institutionalized_connection）",
    "beta_id":       "institutionalized_connection",
    "opportunity":   "MCP対応で長期安定化が実現できる。Relay Pro の差別化要因になる",
    "validated_at":  None,
}


def migrate(db_path: Path = DB_PATH, dry_run: bool = False) -> dict:
    """
    judgement_reason テーブルにカラムを追加する。
    dry_run=True の場合は追加予定カラム名だけ返し、DBを変更しない。
    """
    if not db_path.exists():
        return {"status": "error", "message": f"DB not found: {db_path}"}

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    # 既存カラムを確認
    existing = {row[1] for row in cur.execute("PRAGMA table_info(judgement_reason)").fetchall()}

    to_add = [(col, t) for col, t, *_ in NEW_COLUMNS if col not in existing]

    if dry_run:
        con.close()
        return {
            "status":       "dry_run",
            "existing_cols": sorted(existing),
            "to_add":        [c for c, _ in to_add],
            "already_exist": [col for col, t, *_ in NEW_COLUMNS if col in existing],
        }

    added = []
    for col, col_type in to_add:
        try:
            cur.execute(f"ALTER TABLE judgement_reason ADD COLUMN {col} {col_type}")
            added.append(col)
            print(f"  [ADD] {col} {col_type}")
        except sqlite3.OperationalError as e:
            print(f"  [SKIP] {col}: {e}")

    con.commit()
    con.close()

    ts = datetime.now().isoformat()
    return {
        "status":  "ok",
        "added":   added,
        "skipped": [col for col, t, *_ in NEW_COLUMNS if col not in [a for a in added]],
        "ts":      ts,
    }


def insert_example(db_path: Path = DB_PATH) -> str:
    """デモ用にサンプルレコードを挿入する"""
    con = sqlite3.connect(str(db_path))
    existing_cols = {row[1] for row in con.execute("PRAGMA table_info(judgement_reason)").fetchall()}

    cols = [c for c in EXAMPLE_RECORD if c in existing_cols]
    vals = [EXAMPLE_RECORD[c] for c in cols]

    con.execute(
        f"INSERT OR IGNORE INTO judgement_reason ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",
        vals
    )
    con.commit()
    rowid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    con.close()
    return f"inserted rowid={rowid}"


def show_schema(db_path: Path = DB_PATH):
    """現在のテーブルスキーマを表示する"""
    con = sqlite3.connect(str(db_path))
    rows = con.execute("PRAGMA table_info(judgement_reason)").fetchall()
    con.close()
    print("\njudgement_reason テーブル スキーマ:")
    for r in rows:
        print(f"  {r[0]:>2} {r[1]:<20} {r[2]}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PHI Decision DNA β拡張マイグレーション")
    parser.add_argument("--dry-run",  action="store_true", help="変更せずに追加予定カラムを表示")
    parser.add_argument("--example",  action="store_true", help="サンプルレコードを挿入")
    parser.add_argument("--schema",   action="store_true", help="現在のスキーマを表示")
    args = parser.parse_args()

    if args.schema:
        show_schema()
        sys.exit(0)

    result = migrate(dry_run=args.dry_run)
    print(f"\n[PHI DNA Migrate] {result}")

    if not args.dry_run and result.get("added"):
        show_schema()

    if args.example and not args.dry_run:
        r = insert_example()
        print(f"[PHI DNA Migrate] サンプルレコード: {r}")
