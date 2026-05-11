"""
guidelines_reviewer.py
MoCKA Guidelines 選別ツール v1.0
=====================================
usage:
    python guidelines_reviewer.py

操作:
    k  → keep（採用）
    s  → skip（不採用）
    e  → edit（内容を編集して採用）
    q  → quit（進捗保存して終了）
    b  → back（1件戻る）
    ?  → 現在の進捗表示

配置先: C:\\Users\\sirok\\MoCKA\\interface\\guidelines_reviewer.py
入力:   C:\\Users\\sirok\\MoCKA\\data\\guidelines.json
DB:     C:\\Users\\sirok\\MoCKA\\data\\mocka_events.db
        → guidelines_reviewed テーブルに保存
"""

import json
import sqlite3
import os
import sys
from datetime import datetime

# ===== パス設定 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOCKA_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

GUIDELINES_JSON = os.path.join(MOCKA_ROOT, "data", "guidelines.json")
DB_PATH         = os.path.join(MOCKA_ROOT, "data", "mocka_events.db")

# ===== DB初期化 =====
def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS guidelines_reviewed (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            source_index  INTEGER UNIQUE,
            category      TEXT,
            content       TEXT,
            edited_content TEXT,
            verdict       TEXT CHECK(verdict IN ('keep','skip','edit')),
            reviewed_at   TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS guidelines_review_progress (
            id            INTEGER PRIMARY KEY CHECK(id=1),
            last_index    INTEGER DEFAULT 0,
            total         INTEGER DEFAULT 0,
            keep_count    INTEGER DEFAULT 0,
            skip_count    INTEGER DEFAULT 0,
            started_at    TEXT,
            updated_at    TEXT
        )
    """)
    conn.commit()

# ===== ガイドライン読み込み =====
def load_guidelines():
    if not os.path.exists(GUIDELINES_JSON):
        print(f"[ERROR] guidelines.json が見つかりません: {GUIDELINES_JSON}")
        print("先に guidelines_engine.py を実行してください。")
        sys.exit(1)

    with open(GUIDELINES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    # guidelines.jsonの構造に応じてフラット化
    items = []
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                items.append({
                    "index": i,
                    "category": item.get("category", item.get("type", "GENERAL")),
                    "content":  item.get("content", item.get("guideline", item.get("text", str(item))))
                })
            else:
                items.append({"index": i, "category": "GENERAL", "content": str(item)})
    elif isinstance(data, dict):
        # {"guidelines": [...]} 形式
        raw = data.get("guidelines", data.get("items", []))
        for i, item in enumerate(raw):
            if isinstance(item, dict):
                items.append({
                    "index": i,
                    "category": item.get("category", item.get("type", "GENERAL")),
                    "content":  item.get("content", item.get("guideline", item.get("text", str(item))))
                })
            else:
                items.append({"index": i, "category": "GENERAL", "content": str(item)})

    return items

# ===== 進捗管理 =====
def get_progress(conn, total):
    row = conn.execute("SELECT * FROM guidelines_review_progress WHERE id=1").fetchone()
    if row is None:
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO guidelines_review_progress(id, last_index, total, keep_count, skip_count, started_at, updated_at)
            VALUES(1, 0, ?, 0, 0, ?, ?)
        """, (total, now, now))
        conn.commit()
        return {"last_index": 0, "total": total, "keep_count": 0, "skip_count": 0}
    return {
        "last_index": row[1], "total": row[2],
        "keep_count": row[3], "skip_count": row[4]
    }

def update_progress(conn, last_index, keep_count, skip_count):
    conn.execute("""
        UPDATE guidelines_review_progress
        SET last_index=?, keep_count=?, skip_count=?, updated_at=?
        WHERE id=1
    """, (last_index, keep_count, skip_count, datetime.now().isoformat()))
    conn.commit()

# ===== 既レビュー済みインデックス取得 =====
def get_reviewed_indices(conn):
    rows = conn.execute("SELECT source_index FROM guidelines_reviewed").fetchall()
    return set(r[0] for r in rows)

# ===== 1件保存 =====
def save_verdict(conn, item, verdict, edited_content=None):
    conn.execute("""
        INSERT OR REPLACE INTO guidelines_reviewed
            (source_index, category, content, edited_content, verdict, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        item["index"],
        item["category"],
        item["content"],
        edited_content,
        verdict,
        datetime.now().isoformat()
    ))
    conn.commit()

# ===== 表示 =====
COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[92m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "gray":   "\033[90m",
    "blue":   "\033[94m",
}

def c(color, text):
    return f"{COLORS.get(color,'')}{text}{COLORS['reset']}"

def print_header(current, total, keep, skip):
    remaining = total - current
    pct = int(current / total * 100) if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)

    print("\n" + "═" * 60)
    print(c("bold", f"  MoCKA Guidelines Reviewer  v1.0"))
    print(f"  [{bar}] {pct}%")
    print(f"  {c('cyan', str(current))}/{total}件  |  "
          f"{c('green', '✓ keep: ' + str(keep))}  "
          f"{c('gray',  '✗ skip: ' + str(skip))}  "
          f"{c('yellow', '残り: ' + str(remaining))}件")
    print("═" * 60)

def print_item(item):
    print(f"\n  {c('blue', '[' + item['category'] + ']')}  "
          f"{c('gray', '#' + str(item['index']))}\n")
    # 長いコンテンツは折り返し表示
    content = item["content"]
    width = 56
    lines = []
    for line in content.split("\n"):
        while len(line) > width:
            lines.append("  " + line[:width])
            line = line[width:]
        lines.append("  " + line)
    print(c("bold", "\n".join(lines)))
    print()

def print_commands():
    print(f"  {c('green','[k]')} keep  "
          f"{c('red','[s]')} skip  "
          f"{c('yellow','[e]')} edit  "
          f"{c('gray','[b]')} back  "
          f"{c('gray','[?]')} 進捗  "
          f"{c('gray','[q]')} 終了")
    print()

# ===== メインループ =====
def main():
    print(c("bold", "\n  MoCKA Guidelines Reviewer 起動中..."))

    guidelines = load_guidelines()
    total = len(guidelines)
    print(f"  guidelines.json: {c('cyan', str(total))} 件読み込み完了")

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    progress    = get_progress(conn, total)
    reviewed    = get_reviewed_indices(conn)
    keep_count  = progress["keep_count"]
    skip_count  = progress["skip_count"]
    cursor      = progress["last_index"]

    # 未レビューのインデックスリストを作成
    pending = [g for g in guidelines if g["index"] not in reviewed]

    if not pending:
        print(c("green", "\n  全件レビュー済みです！"))
        _print_summary(conn, total, keep_count, skip_count)
        conn.close()
        return

    print(f"  未レビュー: {c('yellow', str(len(pending)))} 件  "
          f"(再開位置から継続)\n")

    i = 0  # pending内のカーソル

    while i < len(pending):
        item = pending[i]
        current_num = len(reviewed) + i + 1

        print_header(current_num - 1, total, keep_count, skip_count)
        print_item(item)
        print_commands()

        try:
            cmd = input("  → ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            cmd = "q"

        if cmd == "k":
            save_verdict(conn, item, "keep")
            reviewed.add(item["index"])
            keep_count += 1
            update_progress(conn, current_num, keep_count, skip_count)
            print(c("green", "  ✓ keep — 採用しました"))
            i += 1

        elif cmd == "s":
            save_verdict(conn, item, "skip")
            reviewed.add(item["index"])
            skip_count += 1
            update_progress(conn, current_num, keep_count, skip_count)
            print(c("gray", "  ✗ skip — スキップしました"))
            i += 1

        elif cmd == "e":
            print(c("yellow", "  編集内容を入力してください（空行2連続で確定）:"))
            lines = []
            while True:
                try:
                    line = input("  > ")
                    if line == "" and lines and lines[-1] == "":
                        break
                    lines.append(line)
                except (KeyboardInterrupt, EOFError):
                    break
            edited = "\n".join(lines).strip()
            if edited:
                save_verdict(conn, item, "edit", edited_content=edited)
                reviewed.add(item["index"])
                keep_count += 1
                update_progress(conn, current_num, keep_count, skip_count)
                print(c("yellow", "  ✎ edit — 編集して採用しました"))
                i += 1
            else:
                print(c("gray", "  空のため編集キャンセル"))

        elif cmd == "b":
            if i > 0:
                i -= 1
                # 1件戻す（DBから削除）
                prev_item = pending[i]
                prev_row = conn.execute(
                    "SELECT verdict FROM guidelines_reviewed WHERE source_index=?",
                    (prev_item["index"],)
                ).fetchone()
                if prev_row:
                    if prev_row[0] == "keep" or prev_row[0] == "edit":
                        keep_count -= 1
                    else:
                        skip_count -= 1
                    conn.execute(
                        "DELETE FROM guidelines_reviewed WHERE source_index=?",
                        (prev_item["index"],)
                    )
                    reviewed.discard(prev_item["index"])
                    conn.commit()
                    update_progress(conn, current_num - 2, keep_count, skip_count)
                print(c("yellow", "  ← 1件戻りました"))
            else:
                print(c("gray", "  これ以上戻れません"))

        elif cmd == "?":
            done  = len(reviewed)
            print(f"\n  進捗: {done}/{total}件  keep={keep_count}  skip={skip_count}  残り={total-done}件")

        elif cmd == "q":
            update_progress(conn, len(reviewed), keep_count, skip_count)
            print(c("yellow", f"\n  中断 — 進捗を保存しました（{len(reviewed)}/{total}件完了）"))
            print(c("gray",  "  次回起動時に続きから再開できます\n"))
            conn.close()
            return

        else:
            print(c("gray", "  k/s/e/b/?/q で操作してください"))

    # 全件完了
    update_progress(conn, total, keep_count, skip_count)
    print(c("green", "\n  ✅ 全件レビュー完了！"))
    _print_summary(conn, total, keep_count, skip_count)
    conn.close()

# ===== サマリー表示 =====
def _print_summary(conn, total, keep_count, skip_count):
    print("\n" + "═" * 60)
    print(c("bold", "  レビュー結果サマリー"))
    print("═" * 60)
    print(f"  総件数:    {total}")
    print(f"  {c('green','採用 (keep+edit): ' + str(keep_count))}")
    print(f"  {c('gray', '不採用 (skip):    ' + str(skip_count))}")
    print(f"\n  DBテーブル: guidelines_reviewed")
    print(f"  DB:         mocka_events.db")
    print(f"\n  次のステップ:")
    print(f"  {c('cyan','python interface/guidelines_to_essence.py')}")
    print(f"  → 採用済みをessenceに注入します")
    print("═" * 60 + "\n")

if __name__ == "__main__":
    main()
