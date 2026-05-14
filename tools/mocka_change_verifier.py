"""
mocka_change_verifier.py
========================
MoCKA側の独立検証ツール。
git diffとeventDBを照合し「記録なき変更」を検出する。

Claude側: mocka_file_editor.py（変更前後を自己記録）
MoCKA側: このスクリプト（git diff×eventDB照合で独立検証）
→ 両方一致して初めて「変更が存在する」

使い方:
    python tools/mocka_change_verifier.py          # 直近の変更を検証
    python tools/mocka_change_verifier.py --since 2026-05-14  # 日付指定

配置先: C:\\Users\\sirok\\MoCKA\\tools\\mocka_change_verifier.py
MoCKA-START.bat起動時に自動実行推奨
"""

import subprocess
import sqlite3
import json
import datetime
import sys
import os
import argparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(ROOT_DIR, "data", "mocka_events.db")
REPORT_PATH = os.path.join(ROOT_DIR, "data", "change_verify_report.json")


# ========== git diff で変更ファイル取得 ==========
def get_git_changed_files(since_date=None):
    """git logで変更されたファイル一覧を取得"""
    try:
        if since_date:
            cmd = ["git", "log", "--name-only", "--pretty=format:", f"--since={since_date}"]
        else:
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        
        result = subprocess.run(
            cmd, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8"
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return list(set(files))  # 重複除去
    except Exception as e:
        print(f"[VERIFIER] git error: {e}")
        return []


# ========== eventDBからCHANGE_START/DONE取得 ==========
def get_recorded_changes(since_date=None):
    """eventDBからCHANGE_START/CHANGE_DONEイベントを取得"""
    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        if since_date:
            cur.execute("""
                SELECT event_id, when_ts, title, description
                FROM events
                WHERE (title LIKE 'CHANGE_START%' OR title LIKE 'CHANGE_DONE%'
                    OR title LIKE 'BATCH_START%' OR title LIKE 'BATCH_DONE%')
                AND when_ts >= ?
                ORDER BY when_ts DESC
            """, (since_date,))
        else:
            cur.execute("""
                SELECT event_id, when_ts, title, description
                FROM events
                WHERE (title LIKE 'CHANGE_START%' OR title LIKE 'CHANGE_DONE%'
                    OR title LIKE 'BATCH_START%' OR title LIKE 'BATCH_DONE%')
                ORDER BY when_ts DESC
                LIMIT 100
            """)
        
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows
    except Exception as e:
        print(f"[VERIFIER] db error: {e}")
        return []


# ========== 照合 ==========
def verify_changes(since_date=None):
    print(f"[VERIFIER] MoCKA変更記録二重検証開始 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[VERIFIER] ROOT: {ROOT_DIR}")
    
    # git側の変更ファイル
    git_files = get_git_changed_files(since_date)
    print(f"[VERIFIER] git変更ファイル: {len(git_files)}件")
    
    # eventDB側の記録
    recorded = get_recorded_changes(since_date)
    print(f"[VERIFIER] CHANGE記録イベント: {len(recorded)}件")
    
    # 記録済みファイルを抽出
    recorded_files = set()
    for ev in recorded:
        # where_pathから直接ファイル名取得
        wp = ev.get("where_path", "") or ""
        if wp:
            fname = os.path.basename(wp.replace("\\", "/"))
            if fname:
                recorded_files.add(fname)
        # free_noteとtitleからもファイルパスを抽出
        note = ev.get("free_note", "") or ""
        title = ev.get("title", "") or ""
        for text in [note, title]:
            for part in text.replace("\\", "/").split():
                if ".py" in part or ".json" in part or ".bat" in part or ".md" in part:
                    fname = os.path.basename(part.strip(".,()[]"))
                    if fname:
                        recorded_files.add(fname)
    
    # 照合: git変更ファイルのうちeventDBに記録がないもの
    unrecorded = []
    for f in git_files:
        fname = os.path.basename(f)
        if fname not in recorded_files:
            unrecorded.append(f)
    
    # 結果レポート
    report = {
        "verified_at": datetime.datetime.now().isoformat(),
        "since_date": since_date,
        "git_changed_count": len(git_files),
        "recorded_event_count": len(recorded),
        "unrecorded_changes": unrecorded,
        "unrecorded_count": len(unrecorded),
        "status": "CLEAN" if not unrecorded else "WARNING",
        "git_files": git_files,
        "recorded_files": list(recorded_files),
    }
    
    # レポート保存
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 結果表示
    print(f"\n{'='*50}")
    print(f"[VERIFIER] 検証結果: {report['status']}")
    print(f"  git変更: {len(git_files)}件")
    print(f"  CHANGE記録: {len(recorded)}件")
    print(f"  未記録変更: {len(unrecorded)}件")
    
    if unrecorded:
        print(f"\n[VERIFIER] ⚠️ 未記録変更ファイル:")
        for f in unrecorded:
            print(f"  - {f}")
        print(f"\n[VERIFIER] → mocka_file_editor.pyで遡及記録を推奨")
        
        # app.pyにWARNINGイベントを送信
        _send_warning_event(unrecorded)
    else:
        print(f"\n[VERIFIER] ✅ 全変更が記録済みです")
    
    print(f"{'='*50}")
    print(f"[VERIFIER] レポート: {REPORT_PATH}")
    return report


# ========== WARNINGイベント送信 ==========
def _send_warning_event(unrecorded_files):
    """未記録変更をMoCKAイベントとして記録"""
    try:
        import urllib.request
        payload = json.dumps({
            "title": f"WARNING: 未記録変更検出 {len(unrecorded_files)}件",
            "description": f"【MoCKA側検証で未記録変更を検出】\n未記録ファイル:\n" + 
                          "\n".join(f"- {f}" for f in unrecorded_files) +
                          "\n\nmocka_file_editor.pyで遡及記録してください。",
            "why_purpose": "二重保証機構によるMoCKA側独立検証",
            "how_trigger": "mocka_change_verifier.py自動実行",
            "tags": "WARNING,未記録変更,二重保証,change_verifier",
            "author": "MoCKA_VERIFIER",
        }).encode("utf-8")
        
        req = urllib.request.Request(
            "http://localhost:5000/public/write_event",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            result = json.loads(resp.read())
            print(f"[VERIFIER] WARNINGイベント記録: {result.get('event_id')}")
    except Exception as e:
        print(f"[VERIFIER] イベント送信失敗（サーバー未起動?）: {e}")


# ========== CLI ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoCKA変更記録二重検証ツール")
    parser.add_argument("--since", default=None, help="検証開始日 例: 2026-05-14")
    args = parser.parse_args()
    
    since = args.since
    if not since:
        # デフォルト: 今日
        since = datetime.datetime.now().strftime("%Y-%m-%d")
    
    report = verify_changes(since_date=since)
    
    # 未記録変更があれば終了コード1
    sys.exit(1 if report["unrecorded_count"] > 0 else 0)
