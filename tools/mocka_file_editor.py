"""
mocka_file_editor.py — MoCKA強制記録ラッパー
============================================
ファイルを変更する前後に自動でMoCKAイベントを記録する。
「戻れる文化」の実装。Gitと同じ思想をMoCKAイベントDBで実現。

使い方:
    python mocka_file_editor.py \
        --file "C:\\Users\\sirok\\MoCKA\\app.py" \
        --old  "if True:" \
        --new  "_seal_running[0] = True" \
        --why  "CPU100%再発防止。_seal_runningフラグが未設定だった" \
        --who  "Claude"

配置先: C:\\Users\\sirok\\MoCKA\\tools\\mocka_file_editor.py
"""

import argparse
import json
import urllib.request
import urllib.error
import hashlib
import datetime
import os
import sys

# ========== 設定 ==========
MCP_URL = "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev"
LOCAL_URL = "http://localhost:5000"
CONTEXT_LINES = 5  # 前後何行を記録するか


# ========== MoCKAイベント記録 ==========
def write_event(title, description, why_purpose, how_trigger, tags, author="Claude"):
    """app.py /write_eventエンドポイント経由でイベント記録"""
    payload = {
        "title": title,
        "description": description,
        "why_purpose": why_purpose,
        "how_trigger": how_trigger,
        "tags": tags,
        "author": author,
        "what_type": "file_change",
        "where_component": "file_system",
        "risk_level": "normal",
    }
    for base_url in [LOCAL_URL, MCP_URL]:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{base_url}/write_event",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                return result.get("event_id", "unknown")
        except Exception as e:
            continue
    return "OFFLINE"


# ========== ファイルハッシュ ==========
def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception:
        return "N/A"


# ========== コンテキスト抽出 ==========
def get_context(lines, idx, n=CONTEXT_LINES):
    start = max(0, idx - n)
    end = min(len(lines), idx + n + 1)
    numbered = []
    for i in range(start, end):
        marker = ">>>" if i == idx else "   "
        numbered.append(f"{marker} L{i+1:4d}: {lines[i].rstrip()}")
    return "\n".join(numbered)


# ========== メイン処理 ==========
def edit_file(file_path, old_str, new_str, why, who="Claude", dry_run=False):
    if not os.path.exists(file_path):
        print(f"[ERROR] ファイルが存在しません: {file_path}")
        sys.exit(1)

    # --- 変更前の状態を取得 ---
    with open(file_path, encoding="utf-8") as f:
        original = f.read()

    lines = original.splitlines()

    if old_str not in original:
        print(f"[ERROR] 対象文字列が見つかりません")
        print(f"  対象: {repr(old_str[:80])}")
        sys.exit(1)

    # 変更行番号を特定
    old_line_idx = None
    for i, line in enumerate(lines):
        if old_str in line:
            old_line_idx = i
            break

    before_hash = file_hash(file_path)
    before_context = get_context(lines, old_line_idx) if old_line_idx is not None else "N/A"
    line_num = (old_line_idx + 1) if old_line_idx is not None else "不明"

    # --- 変更後の状態を計算 ---
    new_content = original.replace(old_str, new_str, 1)
    new_lines = new_content.splitlines()

    new_line_idx = None
    for i, line in enumerate(new_lines):
        if new_str.split("\n")[0] in line:
            new_line_idx = i
            break
    after_context = get_context(new_lines, new_line_idx) if new_line_idx is not None else "N/A"

    # ========== STEP 1: 変更前イベント記録 ==========
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pre_description = f"""【変更着手前記録】
WHO  : {who}
WHAT : {os.path.basename(file_path)} L{line_num} の変更
WHERE: {file_path}
WHEN : {now}
WHY  : {why}
HOW  : mocka_file_editor.py による制度的変更

【変更前コード】(L{line_num}付近)
{before_context}

【変更内容】
- 変更前: {repr(old_str[:200])}
+ 変更後: {repr(new_str[:200])}

【変更前ハッシュ】{before_hash}"""

    if not dry_run:
        pre_event_id = write_event(
            title=f"CHANGE_START: {os.path.basename(file_path)} L{line_num} — {why[:50]}",
            description=pre_description,
            why_purpose=why,
            how_trigger="mocka_file_editor.py 変更着手前自動記録",
            tags=f"FILE_CHANGE,PRE,{os.path.basename(file_path)}",
            author=who,
        )
        print(f"[MoCKA] 変更前記録: {pre_event_id}")
    else:
        print(f"[DRY-RUN] 変更前記録をスキップ")
        pre_event_id = "DRY_RUN"

    # ========== STEP 2: ファイル変更実施 ==========
    if not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[EDIT] {file_path} L{line_num} を変更しました")
    else:
        print(f"[DRY-RUN] ファイル変更をスキップ")

    # ========== STEP 3: 変更後イベント記録 ==========
    after_hash = file_hash(file_path) if not dry_run else "DRY_RUN"
    post_description = f"""【変更完了記録】
WHO  : {who}
WHAT : {os.path.basename(file_path)} L{line_num} の変更完了
WHERE: {file_path}
WHEN : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
WHY  : {why}

【変更後コード】(変更箇所付近)
{after_context}

【差分サマリー】
- 変更前: {repr(old_str[:200])}
+ 変更後: {repr(new_str[:200])}

【ハッシュ変化】
  Before: {before_hash}
  After : {after_hash}

【参照イベント】{pre_event_id}"""

    if not dry_run:
        post_event_id = write_event(
            title=f"CHANGE_DONE: {os.path.basename(file_path)} L{line_num} — {why[:50]}",
            description=post_description,
            why_purpose=why,
            how_trigger="mocka_file_editor.py 変更完了後自動記録",
            tags=f"FILE_CHANGE,POST,FIX,{os.path.basename(file_path)}",
            author=who,
        )
        print(f"[MoCKA] 変更後記録: {post_event_id}")
    else:
        print(f"[DRY-RUN] 変更後記録をスキップ")
        post_event_id = "DRY_RUN"

    print(f"\n[完了] {file_path}")
    print(f"  変更前イベント: {pre_event_id}")
    print(f"  変更後イベント: {post_event_id}")
    print(f"  変更行      : L{line_num}")
    print(f"  Before hash : {before_hash}")
    print(f"  After hash  : {after_hash}")

    return pre_event_id, post_event_id


# ========== 複数変更バッチ ==========
def edit_file_batch(file_path, changes, why, who="Claude"):
    """
    複数箇所を一括変更する。
    changes = [{"old": "...", "new": "..."}, ...]
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] ファイルが存在しません: {file_path}")
        sys.exit(1)

    with open(file_path, encoding="utf-8") as f:
        original = f.read()

    before_hash = file_hash(file_path)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 変更前記録
    changes_summary = "\n".join([
        f"  [{i+1}] - {repr(c['old'][:60])}\n       + {repr(c['new'][:60])}"
        for i, c in enumerate(changes)
    ])
    pre_description = f"""【バッチ変更着手前記録】
WHO  : {who}
WHAT : {os.path.basename(file_path)} {len(changes)}箇所の変更
WHERE: {file_path}
WHEN : {now}
WHY  : {why}

【変更内容一覧】
{changes_summary}

【変更前ハッシュ】{before_hash}"""

    pre_event_id = write_event(
        title=f"BATCH_START: {os.path.basename(file_path)} {len(changes)}箇所 — {why[:40]}",
        description=pre_description,
        why_purpose=why,
        how_trigger="mocka_file_editor.py バッチ変更着手前",
        tags=f"FILE_CHANGE,BATCH,PRE,{os.path.basename(file_path)}",
        author=who,
    )
    print(f"[MoCKA] バッチ変更前記録: {pre_event_id}")

    # 変更実施
    new_content = original
    applied = 0
    for c in changes:
        if c["old"] in new_content:
            new_content = new_content.replace(c["old"], c["new"], 1)
            applied += 1
        else:
            print(f"[WARN] 対象なし: {repr(c['old'][:60])}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[EDIT] {applied}/{len(changes)}箇所を変更しました")

    after_hash = file_hash(file_path)

    # 変更後記録
    post_event_id = write_event(
        title=f"BATCH_DONE: {os.path.basename(file_path)} {applied}箇所完了 — {why[:40]}",
        description=f"""【バッチ変更完了記録】
適用: {applied}/{len(changes)}箇所
Before: {before_hash}
After : {after_hash}
参照  : {pre_event_id}

{changes_summary}""",
        why_purpose=why,
        how_trigger="mocka_file_editor.py バッチ変更完了後",
        tags=f"FILE_CHANGE,BATCH,POST,{os.path.basename(file_path)}",
        author=who,
    )
    print(f"[MoCKA] バッチ変更後記録: {post_event_id}")
    return pre_event_id, post_event_id


# ========== CLI ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoCKA強制記録ファイル編集ツール")
    parser.add_argument("--file", required=True, help="編集対象ファイルパス")
    parser.add_argument("--old",  required=True, help="変更前の文字列")
    parser.add_argument("--new",  required=True, help="変更後の文字列")
    parser.add_argument("--why",  required=True, help="変更理由（WHY）")
    parser.add_argument("--who",  default="Claude", help="変更者（WHO）")
    parser.add_argument("--dry-run", action="store_true", help="実際には変更せず記録内容を確認")

    args = parser.parse_args()
    edit_file(
        file_path=args.file,
        old_str=args.old,
        new_str=args.new,
        why=args.why,
        who=args.who,
        dry_run=args.dry_run,
    )
