import time, os, sys, json, subprocess, sqlite3, hashlib, requests
from pathlib import Path
from datetime import datetime, date

# ===== 設定 =====
RAW_DIR        = Path("C:/Users/sirok/MoCKA/data/storage/infield/RAW")
CALIBER_URL    = "http://localhost:5679"
DB_PATH        = Path("C:/Users/sirok/MoCKA/data/events.db")
ESSENCE_SCRIPT = "C:/Users/sirok/MoCKA/essence_classifier.py"
PING_SCRIPT    = "C:/Users/sirok/MoCKA/ping_generator.py"
MOCKA_DIR      = "C:/Users/sirok/MoCKA"
POLL_INTERVAL  = 60   # 秒
SEAL_HOUR      = 3    # 日次seal実行時刻（3時）

processed  = set()
last_seal_date = None

# ===== ② BOM除去 + JSON検証 =====
def remove_bom_and_validate(path: Path):
    raw = path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
        path.write_bytes(raw)
    try:
        return json.loads(raw.decode("utf-8")), True
    except Exception as e:
        print(f"[INVALID JSON] {path.name}: {e}")
        return None, False

# ===== ③ caliber_server投入 =====
def submit_to_caliber(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            r = requests.post(f"{CALIBER_URL}/ingest",
                              files={"file": f}, timeout=120)
        if r.status_code == 200:
            print(f"[③ caliber OK] {path.name}")
            return True
        print(f"[③ caliber NG] {r.status_code} {r.text[:80]}")
        return False
    except Exception as e:
        print(f"[③ caliber ERROR] {e}")
        return False

# ===== ④⑤ スクリプト実行 =====
def run_script(script: str, label: str):
    try:
        subprocess.run(["python", script], check=True, cwd=MOCKA_DIR)
        print(f"[{label} OK]")
    except Exception as e:
        print(f"[{label} ERROR] {e}")

# ===== ⑥ events.db記録 =====
def record_to_db(path: Path, data: dict):
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS watchdog_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                filename  TEXT,
                sha256    TEXT,
                event_id  TEXT,
                status    TEXT
            )
        """)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        eid = data.get("event_id", "")
        cur.execute(
            "INSERT INTO watchdog_log(ts,filename,sha256,event_id,status) VALUES(?,?,?,?,?)",
            (ts, path.name, sha, eid, "processed")
        )
        con.commit()
        con.close()
        print(f"[⑥ DB記録] {path.name}")
    except Exception as e:
        print(f"[⑥ DB ERROR] {e}")

# ===== ⑦ 日次seal =====
def try_daily_seal():
    global last_seal_date
    now = datetime.now()
    if now.hour == SEAL_HOUR and now.date() != last_seal_date:
        # TODO_427, IC_20260708_001是正(監査官R01承認パック1):
        # anchor_update.pyの自動実行はHuman Gateを迂回するため廃止。
        # app.py側の日次AUTO_SEAL分岐(auto_audit_loop)と対称的に、PENDING
        # イベントを記録して停止するのみとし、実際のseal実行はきむら博士の
        # 明示指示(human_gate_override_event_id付与)による手動実行でのみ行う。
        try:
            if MOCKA_DIR not in sys.path:
                sys.path.insert(0, MOCKA_DIR)
            from interface.event_buffer import get_buffer
            get_buffer().push({
                "event_id": f"AUTO_SEAL_PENDING_DAILY_{now.strftime('%Y%m%d%H%M%S')}",
                "when": now.isoformat(),
                "who_actor": "system:watchdog_mocka",
                "what_type": "AUTO_SEAL_PENDING_DAILY",
                "where_component": "watchdog_mocka.py:try_daily_seal",
                "where_path": "scripts/ledger/anchor_update.py",
                "why_purpose": "日次(SEAL_HOUR時)seal要求。自動実行はしない(Human Gate迂回防止、TODO_427/IC_20260708_001是正)。",
                "how_trigger": f"daily_condition date={now.date().isoformat()}",
                "channel_type": "internal",
                "lifecycle_phase": "in_operation",
                "risk_level": "normal",
                "category_ab": "B",
                "target_class": "governance",
                "title": "AUTO_SEAL_PENDING_DAILY: 日次seal条件成立(watchdog)、seal実行は人間指示待ち",
                "short_summary": f"date={now.date().isoformat()}。anchor_update.pyは自動実行しない。",
                "before_state": "accumulating",
                "after_state": "pending_human_instruction",
                "change_type": "governance",
                "impact_scope": "seal_pipeline",
                "impact_result": "no_auto_execution",
                "related_event_id": "N/A", "trace_id": "N/A",
                "free_note": "require_human_gate=True|source=AUTO_SEAL_DAILY_WATCHDOG",
            })
            print("[⑦ mocka-seal] AUTO_SEAL_PENDING_DAILY記録のみ(自動seal実行なし、人間指示待ち)")
        except Exception as e:
            print(f"[⑦ mocka-seal EVENT ERROR] {e}")
        last_seal_date = now.date()

# ===== メインループ =====
def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[watchdog_mocka] 起動 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  監視: {RAW_DIR}")
    print(f"  DB  : {DB_PATH}")
    print(f"  Poll: {POLL_INTERVAL}秒")

    while True:
        try:
            for f in sorted(RAW_DIR.glob("*.json")):
                if f.name in processed:
                    continue
                print(f"\n[① 検知] {f.name}")
                data, ok = remove_bom_and_validate(f)   # ②
                if not ok:
                    processed.add(f.name)
                    continue
                if submit_to_caliber(f):                 # ③
                    run_script(ESSENCE_SCRIPT, "④ essence_classifier")  # ④
                    run_script(PING_SCRIPT,    "⑤ ping_generator")      # ⑤
                    record_to_db(f, data)                # ⑥
                    processed.add(f.name)
                else:
                    print(f"[SKIP] caliber失敗・次回リトライ: {f.name}")

            try_daily_seal()                             # ⑦

        except Exception as e:
            print(f"[LOOP ERROR] {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
