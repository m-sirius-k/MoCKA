"""
export_for_cloudflare.py
SQLite の events テーブルを JSON に書き出し、
OVERVIEW/TODO/lever_essence を data/ にコピーする。
MoCKA-START.bat から呼び出す。
"""
import json, sqlite3, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

MOCKA_ROOT  = Path(r"C:\Users\sirok\MoCKA")
USER_ROOT   = Path(r"C:\Users\sirok")
DATA_OUT    = MOCKA_ROOT / "data"
DB_PATH     = MOCKA_ROOT / "data" / "mocka_events.db"

COPIES = [
    (USER_ROOT / "MOCKA_OVERVIEW.json",  DATA_OUT / "MOCKA_OVERVIEW.json"),
    (USER_ROOT / "MOCKA_TODO.json",      DATA_OUT / "MOCKA_TODO.json"),
    (MOCKA_ROOT / "interface" / "lever_essence.json",  DATA_OUT / "lever_essence.json"),
]

def export_events():
    if not DB_PATH.exists():
        print(f"[export] DB not found: {DB_PATH}")
        return
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute("SELECT * FROM events ORDER BY rowid DESC LIMIT 200")
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception as e:
        print(f"[export] events query error: {e}")
        rows = []
    finally:
        con.close()
    out = DATA_OUT / "events_latest.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[export] events → {out} ({len(rows)} rows)")

def _inject_snapshot_ts(dst: Path):
    """コピー後のJSONに _snapshot_at フィールドを注入する（正本は変更しない）"""
    try:
        data = json.loads(dst.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            data['_snapshot_at'] = datetime.now(timezone.utc).isoformat()
            dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"[snapshot_ts] skip {dst.name}: {e}")


def _copy_with_retry(src: Path, dst: Path, retries=7, base_delay=0.5):
    for attempt in range(retries):
        try:
            shutil.copy2(src, dst)
            return
        except PermissionError as e:
            if attempt == retries - 1:
                print(f"[copy] giving up on {src.name} -> {dst}: {e}")
                raise
            delay = base_delay * (2 ** attempt)
            print(f"[copy] {dst.name} locked, retry {attempt + 1}/{retries} in {delay}s")
            time.sleep(delay)

def copy_files():
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    for src, dst in COPIES:
        if src.exists():
            try:
                _copy_with_retry(src, dst)
            except PermissionError:
                continue
            _inject_snapshot_ts(dst)
            print(f"[copy] {src.name} → {dst}")
        else:
            print(f"[skip] not found: {src}")

if __name__ == "__main__":
    copy_files()
    export_events()
    print("[export] done")
