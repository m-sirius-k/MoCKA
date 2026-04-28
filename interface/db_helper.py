#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoCKA db_helper.py — SQLite/CSV 併用ブリッジ
Phase 2: app.py / router.py のCSV直書きをこのモジュール経由に統一

設計原則:
  - 書き込み: SQLite + CSV 両方（併用期間）
  - 読み込み: SQLite優先（CSVフォールバック）
  - 整合性確認後: CSV_WRITE_ENABLED = False に切替

配置先: C:/Users/sirok/MoCKA/interface/db_helper.py
"""

import sqlite3
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ============================================================
# 設定
# ============================================================
MOCKA_ROOT  = Path(os.environ.get("MOCKA_ROOT", r"C:\Users\sirok\MoCKA"))
DB_PATH     = MOCKA_ROOT / "data" / "mocka_events.db"
CSV_PATH    = MOCKA_ROOT / "data" / "events.csv"

# 併用期間フラグ
# True  = SQLite + CSV 両方に書く（Phase 2移行期）
# False = SQLite のみ（Phase 3完了後）
CSV_WRITE_ENABLED = True

# 正規event_idパターン
VALID_ID_RE = re.compile(r'^E\d{8}_\d{3,}$')

# CSVフィールド定義（既存app.pyのFIELDNAMESと同一）
CSV_FIELDNAMES = [
    "event_id", "when", "who_actor", "what_type",
    "where_component", "where_path", "why_purpose", "how_trigger",
    "channel_type", "lifecycle_phase", "risk_level", "category_ab",
    "target_class", "title", "short_summary",
    "before_state", "after_state", "change_type",
    "impact_scope", "impact_result",
    "related_event_id", "trace_id", "free_note",
]

# SQLiteカラム（when_tsにリネーム済み）
DB_FIELDNAMES = [f if f != "when" else "when_ts" for f in CSV_FIELDNAMES]


# ============================================================
# 内部ユーティリティ
# ============================================================
def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_csv_dict(row: dict) -> dict:
    """DBのwhen_ts → CSVのwhen に変換"""
    d = dict(row)
    if "when_ts" in d:
        d["when"] = d.pop("when_ts")
    # 拡張カラムはCSVに書かない
    return {k: d.get(k, "") or "" for k in CSV_FIELDNAMES}


def _ensure_csv():
    """CSVが存在しない場合にヘッダーだけ作成"""
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()


# ============================================================
# PUBLIC API
# ============================================================

def read_events(
    limit: Optional[int] = None,
    what_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    order: str = "DESC",
) -> list[dict]:
    """
    イベント読み込み（SQLite優先）
    app.py の csv.DictReader を置き換え
    """
    if not DB_PATH.exists():
        # フォールバック: CSV読み込み
        return _read_events_csv(limit=limit)

    conn = _get_conn()
    where_clauses = []
    params = []

    if what_type:
        where_clauses.append("what_type = ?")
        params.append(what_type)
    if risk_level:
        where_clauses.append("risk_level = ?")
        params.append(risk_level)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    limit_sql  = f"LIMIT {limit}" if limit else ""
    order_sql  = f"ORDER BY when_ts {order}"

    sql = f"SELECT * FROM events {where_sql} {order_sql} {limit_sql}"
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()

    # when_ts → when に変換（既存コードとの互換性）
    for r in rows:
        if "when_ts" in r:
            r["when"] = r.pop("when_ts")
    return rows


def write_event(row: dict) -> bool:
    """
    イベント書き込み（SQLite + CSV併用）
    app.py の csv.DictWriter.writerow を置き換え

    Args:
        row: CSV_FIELDNAMESに準拠したdict
             ("when" キーを使用、db_helperが内部でwhen_tsに変換)
    Returns:
        True: 成功 / False: 失敗
    """
    if not row.get("event_id"):
        return False

    # ① SQLite書き込み
    db_row = {}
    for csv_col in CSV_FIELDNAMES:
        db_col = "when_ts" if csv_col == "when" else csv_col
        db_row[db_col] = row.get(csv_col) or None

    db_row["_source"] = "new"
    db_row["_imported_at"] = datetime.now(timezone.utc).isoformat()

    try:
        conn = _get_conn()
        conn.execute(
            f"INSERT OR IGNORE INTO events ({', '.join(db_row.keys())}) "
            f"VALUES ({', '.join(['?'] * len(db_row))})",
            list(db_row.values())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[db_helper] SQLite書き込みエラー: {e}")
        return False

    # ② CSV書き込み（併用期間のみ）
    if CSV_WRITE_ENABLED:
        try:
            _ensure_csv()
            with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                csv_row = {k: row.get(k, "") for k in CSV_FIELDNAMES}
                writer.writerow(csv_row)
        except Exception as e:
            print(f"[db_helper] CSV書き込みエラー（SQLiteは成功済み）: {e}")
            # SQLiteに書けていればCSV失敗は致命的ではない

    return True


def count_events(
    what_type: Optional[str] = None,
    risk_level: Optional[str] = None,
) -> int:
    """
    イベント件数取得（SQLite優先）
    app.py の len(list(csv.DictReader(f))) を置き換え
    """
    if not DB_PATH.exists():
        return _count_events_csv()

    conn = _get_conn()
    where_clauses = []
    params = []
    if what_type:
        where_clauses.append("what_type = ?")
        params.append(what_type)
    if risk_level:
        where_clauses.append("risk_level = ?")
        params.append(risk_level)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    count = conn.execute(f"SELECT COUNT(*) FROM events {where_sql}", params).fetchone()[0]
    conn.close()
    return count


def get_event(event_id: str) -> Optional[dict]:
    """特定event_idのイベントを取得"""
    if not DB_PATH.exists():
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM events WHERE event_id = ?", (event_id,)
    ).fetchone()
    conn.close()
    if row:
        r = dict(row)
        if "when_ts" in r:
            r["when"] = r.pop("when_ts")
        return r
    return None


def search_events(keyword: str, limit: int = 50) -> list[dict]:
    """
    キーワード検索（title / short_summary / free_note）
    app.py の866行付近のCSV検索を置き換え
    """
    if not DB_PATH.exists():
        return []
    conn = _get_conn()
    rows = [dict(r) for r in conn.execute(
        """SELECT * FROM events
           WHERE title LIKE ? OR short_summary LIKE ? OR free_note LIKE ?
           ORDER BY when_ts DESC LIMIT ?""",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit)
    ).fetchall()]
    conn.close()
    for r in rows:
        if "when_ts" in r:
            r["when"] = r.pop("when_ts")
    return rows


def get_next_event_id() -> str:
    """
    次のevent_idを採番（E{YYYYMMDD}_{NNN}形式）
    router.pyのget_next_event_id()を置き換え可能
    """
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"

    if DB_PATH.exists():
        conn = _get_conn()
        rows = conn.execute(
            "SELECT event_id FROM events WHERE event_id LIKE ? ORDER BY event_id DESC LIMIT 1",
            (f"{prefix}%",)
        ).fetchall()
        conn.close()
        if rows:
            last_id = rows[0][0]
            num = int(last_id.split("_")[-1]) + 1
            return f"{prefix}{num:03d}"

    return f"{prefix}001"


# ============================================================
# フォールバック（CSV読み込み）
# ============================================================
def _read_events_csv(limit=None) -> list[dict]:
    if not CSV_PATH.exists():
        return []
    try:
        with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        return rows[:limit] if limit else rows
    except Exception:
        return []


def _count_events_csv() -> int:
    if not CSV_PATH.exists():
        return 0
    try:
        with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
            return sum(1 for _ in csv.DictReader(f))
    except Exception:
        return 0


# ============================================================
# 動作確認
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("db_helper 動作確認")
    print("=" * 50)
    print(f"DB:  {DB_PATH} ({'exists' if DB_PATH.exists() else 'NOT FOUND'})")
    print(f"CSV: {CSV_PATH} ({'exists' if CSV_PATH.exists() else 'NOT FOUND'})")
    print(f"CSV_WRITE_ENABLED: {CSV_WRITE_ENABLED}")
    print()

    count = count_events()
    print(f"総イベント数: {count}")

    latest = read_events(limit=3, order="DESC")
    print(f"\n最新3件:")
    for r in latest:
        print(f"  {r.get('event_id')} | {r.get('when','')[:10]} | {r.get('what_type')} | {r.get('title','')[:30]}")

    next_id = get_next_event_id()
    print(f"\n次のevent_id: {next_id}")

    print("\n[OK] db_helper 動作確認完了")
