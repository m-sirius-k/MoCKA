"""
mocka_change_verifier.py
MoCKA側独立検証ツール。git diff×eventDB照合で未記録変更を検出。
"""
import subprocess, sqlite3, json, datetime, sys, os, argparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(ROOT_DIR, "data", "mocka_events.db")
REPORT_PATH = os.path.join(ROOT_DIR, "data", "change_verify_report.json")

def get_git_changed_files(since_date=None):
    try:
        cmd = ["git","log","--name-only","--pretty=format:",f"--since={since_date}"] if since_date else ["git","diff","--name-only","HEAD~1","HEAD"]
        r = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8")
        return list(set([f.strip() for f in r.stdout.splitlines() if f.strip()]))
    except Exception as e:
        print(f"[VERIFIER] git error: {e}"); return []

def get_recorded_changes(since_date=None):
    try:
        con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row; cur = con.cursor()
        if since_date:
            cur.execute("""SELECT event_id,when_ts,title,free_note,where_path FROM events
                WHERE (title LIKE 'CHANGE_START%' OR title LIKE 'CHANGE_DONE%'
                    OR title LIKE 'BATCH_START%' OR title LIKE 'BATCH_DONE%')
                AND when_ts >= ? ORDER BY when_ts DESC""", (since_date,))
        else:
            cur.execute("""SELECT event_id,when_ts,title,free_note,where_path FROM events
                WHERE (title LIKE 'CHANGE_START%' OR title LIKE 'CHANGE_DONE%'
                    OR title LIKE 'BATCH_START%' OR title LIKE 'BATCH_DONE%')
                ORDER BY when_ts DESC LIMIT 100""")
        rows = [dict(r) for r in cur.fetchall()]; con.close(); return rows
    except Exception as e:
        print(f"[VERIFIER] db error: {e}"); return []

def verify_changes(since_date=None):
    print(f"[VERIFIER] 二重検証開始 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    git_files = get_git_changed_files(since_date)
    print(f"[VERIFIER] git変更: {len(git_files)}件")
    recorded = get_recorded_changes(since_date)
    print(f"[VERIFIER] CHANGE記録: {len(recorded)}件")

    recorded_files = set()
    for ev in recorded:
        wp = ev.get("where_path","") or ""
        if wp: recorded_files.add(os.path.basename(wp.replace("\\","/")))
        for text in [ev.get("free_note","") or "", ev.get("title","") or ""]:
            for part in text.replace("\\","/").split():
                part = part.strip(".,()[]\"'")
                if any(part.endswith(x) for x in [".py",".json",".bat",".md",".js"]):
                    recorded_files.add(os.path.basename(part))

    unrecorded = [f for f in git_files if os.path.basename(f) not in recorded_files]
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
    with open(REPORT_PATH,"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)

    print(f"\n{'='*50}")
    print(f"[VERIFIER] 結果: {report['status']}")
    print(f"  git変更: {len(git_files)}件 / CHANGE記録: {len(recorded)}件 / 未記録: {len(unrecorded)}件")
    if recorded_files: print(f"  記録済: {', '.join(list(recorded_files)[:5])}")
    if unrecorded:
        print(f"\n[VERIFIER] ⚠️ 未記録変更:")
        for f in unrecorded: print(f"  - {f}")
        _send_warning(unrecorded)
    else:
        print(f"\n[VERIFIER] ✅ 全変更が記録済みです")
    print(f"{'='*50}")
    return report

def _send_warning(files):
    try:
        import urllib.request
        payload = json.dumps({"title":f"WARNING: 未記録変更検出 {len(files)}件",
            "free_note":"未記録: "+",".join(files),
            "why_purpose":"二重保証検証","how_trigger":"mocka_change_verifier.py",
            "tags":"WARNING,未記録変更","author":"MoCKA_VERIFIER"}).encode("utf-8")
        req = urllib.request.Request("http://localhost:5000/public/write_event",
            data=payload,headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=3) as resp:
            print(f"[VERIFIER] WARNING記録: {json.loads(resp.read()).get('event_id')}")
    except Exception as e:
        print(f"[VERIFIER] 送信失敗: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default=None)
    args = parser.parse_args()
    since = args.since or datetime.datetime.now().strftime("%Y-%m-%d")
    report = verify_changes(since_date=since)
    sys.exit(1 if report["unrecorded_count"] > 0 else 0)
