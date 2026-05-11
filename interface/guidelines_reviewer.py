"""
guidelines_reviewer.py
MoCKA Guidelines 選別ツール v1.1
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
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MOCKA_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

GUIDELINES_JSON = os.path.join(MOCKA_ROOT, "data", "guidelines.json")
DB_PATH         = os.path.join(MOCKA_ROOT, "data", "mocka_events.db")

# ===== カラー =====
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[92m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "gray":   "\033[90m",
    "blue":   "\033[94m",
    "white":  "\033[97m",
}
def c(color, text): return f"{C.get(color,'')}{text}{C['reset']}"

# ===== DB初期化 =====
def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS guidelines_reviewed (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            source_index   INTEGER UNIQUE,
            gl_id          TEXT,
            category       TEXT,
            score          REAL,
            source_text    TEXT,
            action_summary TEXT,
            cause_who      TEXT,
            cause_what     TEXT,
            cause_why      TEXT,
            prevent_how    TEXT,
            edited_content TEXT,
            verdict        TEXT CHECK(verdict IN ('keep','skip','edit')),
            reviewed_at    TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS guidelines_review_progress (
            id          INTEGER PRIMARY KEY CHECK(id=1),
            last_index  INTEGER DEFAULT 0,
            total       INTEGER DEFAULT 0,
            keep_count  INTEGER DEFAULT 0,
            skip_count  INTEGER DEFAULT 0,
            started_at  TEXT,
            updated_at  TEXT
        )
    """)
    conn.commit()

# ===== ガイドライン読み込み・パース =====
def load_guidelines():
    if not os.path.exists(GUIDELINES_JSON):
        print(f"[ERROR] guidelines.json が見つかりません: {GUIDELINES_JSON}")
        sys.exit(1)

    with open(GUIDELINES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    raw = data if isinstance(data, list) else data.get("guidelines", data.get("items", []))

    items = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            items.append({"index": i, "gl_id": "", "category": "GENERAL",
                          "score": 0.0, "source_text": str(item),
                          "action_summary": "", "cause_who": "", "cause_what": "",
                          "cause_why": "", "prevent_how": ""})
            continue

        cause   = item.get("cause_5w1h", {})    or {}
        prevent = item.get("prevention_5w1h", {}) or {}
        action  = item.get("action_directive", "") or ""

        # action_directive → 表示用サマリー抽出
        action_clean = action.replace("\n", " ").strip()
        if "→" in action_clean:
            action_summary = action_clean.split("→")[-1].strip()
        else:
            action_summary = action_clean[:120]

        source_text = (cause.get("source_text", "") or
                       item.get("source_text", "") or "").strip()

        items.append({
            "index":          i,
            "gl_id":          item.get("id", ""),
            "category":       item.get("category", "GENERAL"),
            "score":          float(item.get("score", item.get("trust_score", 0.0)) or 0.0),
            "source_text":    source_text[:200],
            "action_summary": action_summary[:150],
            "cause_who":      cause.get("who", ""),
            "cause_what":     cause.get("what", ""),
            "cause_why":      cause.get("why", ""),
            "prevent_how":    prevent.get("how", ""),
        })

    return items

# ===== 進捗管理 =====
def get_progress(conn, total):
    row = conn.execute("SELECT * FROM guidelines_review_progress WHERE id=1").fetchone()
    if row is None:
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO guidelines_review_progress
                (id,last_index,total,keep_count,skip_count,started_at,updated_at)
            VALUES(1,0,?,0,0,?,?)
        """, (total, now, now))
        conn.commit()
        return {"last_index": 0, "total": total, "keep_count": 0, "skip_count": 0}
    return {"last_index": row[1], "total": row[2],
            "keep_count": row[3], "skip_count": row[4]}

def update_progress(conn, last_index, keep_count, skip_count):
    conn.execute("""
        UPDATE guidelines_review_progress
        SET last_index=?, keep_count=?, skip_count=?, updated_at=?
        WHERE id=1
    """, (last_index, keep_count, skip_count, datetime.now().isoformat()))
    conn.commit()

def get_reviewed_indices(conn):
    rows = conn.execute("SELECT source_index FROM guidelines_reviewed").fetchall()
    return set(r[0] for r in rows)

# ===== 1件保存 =====
def save_verdict(conn, item, verdict, edited_content=None):
    conn.execute("""
        INSERT OR REPLACE INTO guidelines_reviewed
            (source_index, gl_id, category, score, source_text, action_summary,
             cause_who, cause_what, cause_why, prevent_how,
             edited_content, verdict, reviewed_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        item["index"], item["gl_id"], item["category"], item["score"],
        item["source_text"], item["action_summary"],
        item["cause_who"], item["cause_what"], item["cause_why"], item["prevent_how"],
        edited_content, verdict, datetime.now().isoformat()
    ))
    conn.commit()

# ===== 表示ユーティリティ =====
def wrap(text, width=54, indent="    "):
    if not text:
        return ""
    lines = []
    for paragraph in str(text).split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        while len(paragraph) > width:
            lines.append(indent + paragraph[:width])
            paragraph = paragraph[width:]
        if paragraph:
            lines.append(indent + paragraph)
    return "\n".join(lines)

def print_header(current, total, keep, skip):
    pct    = int(current / total * 100) if total > 0 else 0
    filled = int(30 * current / total)  if total > 0 else 0
    bar    = "█" * filled + "░" * (30 - filled)
    print("\n" + "═" * 62)
    print(c("bold", "  MoCKA Guidelines Reviewer  v1.1"))
    print(f"  [{bar}] {pct}%  {c('cyan', str(current))}/{total}件")
    print(f"  {c('green','✓ 採用: '+str(keep))}   "
          f"{c('gray', '✗ 除外: '+str(skip))}   "
          f"{c('yellow','残り: '+str(total - current)+'件')}")
    print("═" * 62)

def print_item(item):
    score       = item["score"]
    score_bar   = "▓" * int(score * 10) + "░" * (10 - int(score * 10))
    score_color = "green" if score >= 0.6 else ("yellow" if score >= 0.4 else "gray")

    print(f"\n  {c('bold', c('blue', '[' + item['category'] + ']'))}  "
          f"#{item['index']}   "
          f"スコア {c(score_color, score_bar)} {score:.2f}")
    print()

    # 元テキスト
    if item["source_text"]:
        print(c("gray",  "  ┌─ 元データ " + "─" * 40))
        print(c("white", wrap(item["source_text"])))
        print(c("gray",  "  └" + "─" * 51))
        print()

    # 原因 5W1H
    rows = [("WHO",  item["cause_who"]),
            ("WHAT", item["cause_what"]),
            ("WHY",  item["cause_why"])]
    if any(v for _, v in rows):
        print(c("gray", "  ┌─ 原因 " + "─" * 44))
        for label, val in rows:
            if val:
                print(f"  │  {c('cyan', label+':')} {val}")
        print(c("gray", "  └" + "─" * 51))
        print()

    # 対処アクション
    if item["action_summary"]:
        print(c("gray",   "  ┌─ 対処アクション " + "─" * 36))
        print(c("yellow", wrap(item["action_summary"])))
        print(c("gray",   "  └" + "─" * 51))
        print()

    # 再発防止
    if item["prevent_how"]:
        print(c("gray",  "  ┌─ 再発防止 " + "─" * 42))
        print(c("green", wrap(item["prevent_how"])))
        print(c("gray",  "  └" + "─" * 51))
        print()

def print_commands():
    print(f"  {c('green','[k] keep')}  "
          f"{c('red',   '[s] skip')}  "
          f"{c('yellow','[e] edit')}  "
          f"{c('gray',  '[b] back   [?] 進捗   [q] 終了')}")
    print()

# ===== メインループ =====
def main():
    print(c("bold", "\n  MoCKA Guidelines Reviewer 起動中..."))

    guidelines = load_guidelines()
    total      = len(guidelines)
    print(f"  guidelines.json: {c('cyan', str(total))} 件読み込み完了")

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    progress   = get_progress(conn, total)
    reviewed   = get_reviewed_indices(conn)
    keep_count = progress["keep_count"]
    skip_count = progress["skip_count"]

    pending = [g for g in guidelines if g["index"] not in reviewed]

    if not pending:
        print(c("green", "\n  全件レビュー済みです！"))
        _print_summary(conn, total, keep_count, skip_count)
        conn.close()
        return

    print(f"  未レビュー: {c('yellow', str(len(pending)))} 件\n")

    i = 0
    while i < len(pending):
        item        = pending[i]
        current_num = len(reviewed) + i

        print_header(current_num, total, keep_count, skip_count)
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
            update_progress(conn, current_num + 1, keep_count, skip_count)
            print(c("green", "  ✓ 採用"))
            i += 1

        elif cmd == "s":
            save_verdict(conn, item, "skip")
            reviewed.add(item["index"])
            skip_count += 1
            update_progress(conn, current_num + 1, keep_count, skip_count)
            print(c("gray", "  ✗ 除外"))
            i += 1

        elif cmd == "e":
            print(c("yellow", "  編集内容を入力（空行2連続で確定）:"))
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
                update_progress(conn, current_num + 1, keep_count, skip_count)
                print(c("yellow", "  ✎ 編集採用"))
                i += 1
            else:
                print(c("gray", "  キャンセル"))

        elif cmd == "b":
            if i > 0:
                i -= 1
                prev = pending[i]
                row  = conn.execute(
                    "SELECT verdict FROM guidelines_reviewed WHERE source_index=?",
                    (prev["index"],)
                ).fetchone()
                if row:
                    if row[0] in ("keep", "edit"):
                        keep_count -= 1
                    else:
                        skip_count -= 1
                    conn.execute("DELETE FROM guidelines_reviewed WHERE source_index=?",
                                 (prev["index"],))
                    reviewed.discard(prev["index"])
                    conn.commit()
                    update_progress(conn, current_num - 1, keep_count, skip_count)
                print(c("yellow", "  ← 1件戻りました"))
            else:
                print(c("gray", "  これ以上戻れません"))

        elif cmd == "?":
            done = len(reviewed)
            print(f"\n  進捗: {done}/{total}件  "
                  f"採用={keep_count}  除外={skip_count}  残り={total - done}件")

        elif cmd == "q":
            update_progress(conn, len(reviewed), keep_count, skip_count)
            print(c("yellow", f"\n  保存して終了 ({len(reviewed)}/{total}件完了)\n"))
            conn.close()
            return

        else:
            print(c("gray", "  k / s / e / b / ? / q で操作してください"))

    update_progress(conn, total, keep_count, skip_count)
    print(c("green", "\n  ✅ 全件レビュー完了！"))
    _print_summary(conn, total, keep_count, skip_count)
    conn.close()

# ===== サマリー =====
def _print_summary(conn, total, keep_count, skip_count):
    print("\n" + "═" * 62)
    print(c("bold", "  レビュー完了"))
    print("═" * 62)
    print(f"  総件数:          {total}")
    print(f"  {c('green', '採用 (keep+edit): ' + str(keep_count))}")
    print(f"  {c('gray',  '除外 (skip):      ' + str(skip_count))}")
    print(f"\n  保存先: mocka_events.db → guidelines_reviewed テーブル")
    print(f"\n  次のステップ:")
    print(f"  {c('cyan', 'python interface/guidelines_to_essence.py')}")
    print(f"  → 採用済みを essence に注入します")
    print("═" * 62 + "\n")

if __name__ == "__main__":
    main()
