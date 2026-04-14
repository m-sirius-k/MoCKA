import csv
import shutil
import os
import json
import subprocess
import sys
import requests
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# ===== 自動連続処理 =====
import threading
import time

PILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "storage", "outbox", "PILS")

def auto_process_loop():
    time.sleep(5)
    while True:
        try:
            files = [f for f in os.listdir(PILS_DIR) if f.endswith(".json")]
            if files:
                print("[AUTO] PILSキュー: {}件 → 処理開始".format(len(files)))
                r = requests.post(
                    CALIBER_SERVER + "/process",
                    json={},
                    headers={"Content-Type": "application/json"},
                    timeout=1800
                )
                if r.status_code == 200:
                    result = r.json()
                    rate = result.get("restore_rate", "?")
                    print("[AUTO] 完了 restore_rate={}".format(rate))
                else:
                    print("[AUTO] エラー({}): {}".format(r.status_code, r.text[:80]))
            time.sleep(10)
        except Exception as e:
            print("[AUTO] 例外: {}".format(str(e)[:80]))
            time.sleep(30)

_auto_thread = threading.Thread(target=auto_process_loop, daemon=True)
_auto_thread.start()
# ===== 自動連続処理ここまで =====


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
EVENTS_CSV = os.path.join(DATA_DIR, "events.csv")
BASE_DIR = ROOT_DIR
RECORDS_DIR = os.path.join(BASE_DIR, "records")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OLD_DIR = os.path.join(BASE_DIR, "OLD_FILES")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
STORAGE = os.path.join(DATA_DIR, "storage", "infield")
OUTBOX  = os.path.join(DATA_DIR, "storage", "outbox", "PILS")
CALIBER_SERVER = "http://localhost:5679"

FIELDNAMES = [
    "event_id", "when", "who_actor", "what_type",
    "where_component", "where_path", "why_purpose", "how_trigger",
    "channel_type", "lifecycle_phase", "risk_level",
    "category_ab", "target_class", "title", "short_summary",
    "before_state", "after_state", "change_type",
    "impact_scope", "impact_result", "related_event_id", "trace_id", "free_note",
]


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "master"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "summary"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "context"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "audit"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "structured"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "timeline"), exist_ok=True)
    os.makedirs(OLD_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "decisions"), exist_ok=True)


def ensure_events_csv():
    ensure_dirs()
    if not os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    ensure_events_csv()
    last_n = 0
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ev = (r.get("event_id") or "").strip()
            if ev.startswith(prefix):
                parts = ev.split("_")
                if len(parts) == 2:
                    try:
                        n = int(parts[1])
                        if n > last_n:
                            last_n = n
                    except ValueError:
                        pass
    return f"{prefix}{last_n+1:03d}"


def append_event(meta: dict):
    ensure_events_csv()
    row = {key: "N/A" for key in FIELDNAMES}
    for k, v in meta.items():
        if k in row and v is not None:
            row[k] = str(v)
    if row["event_id"] == "N/A":
        row["event_id"] = next_event_id()
    if row["when"] == "N/A":
        row["when"] = datetime.now().isoformat(timespec="seconds")
    eid = row["event_id"]
    category = row.get("category_ab", "N/A")
    target = row.get("target_class", "N/A")
    master_path = os.path.join(RECORDS_DIR, "master", f"{eid}.json")
    master_obj = {
        "event_id": eid,
        "timestamp": row["when"],
        "what_type": row.get("what_type", "N/A"),
        "status": "recorded",
        "category": category,
        "target": target,
    }
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master_obj, f, ensure_ascii=False, indent=2)
    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def load_history(limit=None):
    ensure_events_csv()
    rows = []
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            clean = {k: (v if v is not None else "") for k, v in r.items()}
            rows.append(clean)
    if limit is not None:
        rows = rows[-int(limit):]
    return rows


def count_layer(layer):
    d = os.path.join(STORAGE, layer)
    if not os.path.exists(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith(".json")])


# =========================
# Flask Routes
# =========================

@app.route("/")
def index():
    return send_from_directory(ROOT_DIR, "index.html")


@app.route("/get_history")
def get_history():
    rows = load_history()
    return jsonify(rows)


@app.route("/caliber/status")
def caliber_status():
    layers = ["RAW", "REDUCED", "RE_REDUCED", "REDUCING", "CORE", "ESSENCE", "RAW_DONE"]
    counts = {layer: count_layer(layer) for layer in layers}
    outbox = len([f for f in os.listdir(OUTBOX) if f.endswith(".json")]) if os.path.exists(OUTBOX) else 0
    counts["outbox_PILS"] = outbox
    try:
        r = requests.get(CALIBER_SERVER + "/health", timeout=2)
        server = "online" if r.status_code == 200 else "error"
    except:
        server = "offline"
    return jsonify({"layers": counts, "caliber_server": server})


@app.route("/caliber/process", methods=["POST"])
def caliber_process():
    try:
        r = requests.post(CALIBER_SERVER + "/process",
            json={}, headers={"Content-Type": "application/json"}, timeout=1800)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/caliber/scan")
def caliber_scan():
    try:
        r = requests.get(CALIBER_SERVER + "/scan", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/orchestra", methods=["POST"])
def orchestra():
    payload = request.get_json(force=True, silent=True) or {}
    prompt = payload.get("prompt", "MoCKA Broadcast")
    mode = payload.get("mode", "orchestra")
    subprocess.Popen(
        [sys.executable, "tools/mocka_orchestra_v10.py", prompt, mode],
        cwd=ROOT_DIR
    )
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(force=True, silent=True) or {}
    c = payload.get("c")
    o = payload.get("o")
    memo = payload.get("memo", "").strip()
    if c not in ("A", "B") or not o:
        return jsonify({"status": "error", "message": "invalid payload"}), 400
    if c == "A":
        what_type = "storage"
        title = f"保存: {o}"
        short_summary = "Storage mission dispatched"
    else:
        what_type = "broadcast"
        title = f"共有: {o}"
        short_summary = "Broadcast mission dispatched"
    meta = {
        "what_type": what_type,
        "category_ab": c,
        "target_class": o,
        "title": title,
        "short_summary": memo if memo else short_summary,
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "where_path": "mocka-extension/background.js",
        "why_purpose": "右クリックメニューからの保存・共有操作",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "before_state": "N/A",
        "after_state": "N/A",
        "change_type": "N/A",
        "impact_scope": "local",
        "impact_result": "N/A",
        "related_event_id": "N/A",
        "trace_id": "N/A",
        "free_note": memo if memo else "N/A",
    }
    append_event(meta)
    return jsonify({"status": "ok"})


@app.route("/collect", methods=["POST"])
def collect():
    import re as _re, csv as _csv, hashlib as _hs, json as _json
    from datetime import datetime, timezone
    from pathlib import Path as P
    d       = request.get_json()
    source  = d.get("source","unknown")
    text    = d.get("text","")
    url     = d.get("url","")
    mode    = d.get("mode","full")
    text    = _re.sub(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}","[EMAIL]",text)
    text    = _re.sub(r"sk-[A-Za-z0-9]{20,}","[APIKEY]",text)
    text    = _re.sub(r"(?i)password\s*[:=]\s*\S+","password=[MASKED]",text)
    if not text: return jsonify({"status":"empty"}),400
    INFIELD = P(r"C:/Users/sirok/MoCKA/data/storage/infield/RAW")
    EVENTS  = P(r"C:/Users/sirok/MoCKA/data/events.csv")
    INFIELD.mkdir(parents=True,exist_ok=True)
    ts      = datetime.now(timezone.utc)
    ts_str  = ts.strftime("%Y-%m-%dT%H:%M:%S")
    ts_f    = ts.strftime("%Y%m%d_%H%M%S")
    rows    = []
    if EVENTS.exists():
        with open(EVENTS, encoding="utf-8", errors="replace") as _f:
            rows = list(_csv.reader(_f))
    prev    = _hs.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"
    eid     = f"ECOL_{ts_f}_{source[:4].upper()}"
    h       = _hs.sha256(f"{eid}{ts_str}{text[:100]}{prev}".encode()).hexdigest()[:16]
    rec     = {"event_id":eid,"source":source,"layer":"RAW","url":url,"mode":mode,
               "text":text,"timestamp":ts_str,"hash":h,"prev_hash":prev,"status":"RAW"}
    fname = INFIELD/f"{ts_f}_{eid}.json"
    _json.dump(rec,open(fname,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    PILS = P(r"C:/Users/sirok/MoCKA/data/storage/outbox/PILS")
    PILS.mkdir(parents=True,exist_ok=True)
    shutil.copy2(fname, PILS/fname.name)
    print(f"[AUTO-PILS] copied to outbox/PILS")
    with open(EVENTS,"a",encoding="utf-8",newline="") as f:
        _csv.writer(f).writerow([eid,ts_str,source,"collect","chat_import","mocka_bridge_v2",
            url[:80],"extension","external","in_operation","normal","A","infield/RAW",
            text[:100].encode("utf-8","replace").decode("utf-8"),prev,"ingest_complete","RAW","local","chat_pipeline","N/A","N/A",
            f"hash={h}|source={source}|mode={mode}"])
    print(f"[COLLECT] {eid} from {source} ({len(text)} chars)")
    return jsonify({"status":"ok","event_id":eid,"hash":h})


@app.route("/caliber/queue")
def caliber_queue():
    import json as _json
    from datetime import datetime
    layers = ["RAW","REDUCED","RE_REDUCED","REDUCING","CORE","ESSENCE","RAW_DONE"]
    counts = {layer: count_layer(layer) for layer in layers}
    outbox = os.path.join(DATA_DIR, "storage", "outbox", "PILS")
    pils_files = []
    if os.path.exists(outbox):
        for f in sorted(os.listdir(outbox)):
            if f.endswith(".json"):
                fpath = os.path.join(outbox, f)
                size = os.path.getsize(fpath)
                pils_files.append({"name": f, "size": size})
    re_reduced_dir = os.path.join(DATA_DIR, "storage", "infield", "RE_REDUCED")
    recent_results = []
    if os.path.exists(re_reduced_dir):
        files = sorted(os.listdir(re_reduced_dir), reverse=True)[:5]
        for f in files:
            try:
                d = _json.load(open(os.path.join(re_reduced_dir, f), encoding="utf-8"))
                recent_results.append({
                    "file": f,
                    "source": d.get("source",""),
                    "restore_rate": d.get("restore_rate", 0),
                    "timestamp": d.get("timestamp",""),
                    "status": d.get("status",""),
                    "preview": d.get("extraction","")[:100]
                })
            except: pass
    reducing_dir = os.path.join(DATA_DIR, "storage", "infield", "REDUCING")
    reducing_results = []
    if os.path.exists(reducing_dir):
        files = sorted(os.listdir(reducing_dir), reverse=True)[:3]
        for f in files:
            try:
                d = _json.load(open(os.path.join(reducing_dir, f), encoding="utf-8"))
                reducing_results.append({
                    "file": f,
                    "restore_rate": d.get("restore_rate", 0),
                    "timestamp": d.get("timestamp","")
                })
            except: pass
    try:
        r = __import__('requests').get("http://localhost:5679/health", timeout=2)
        server = "online"
    except:
        server = "offline"
    return __import__('flask').jsonify({
        "layers": counts,
        "caliber_server": server,
        "queue": pils_files,
        "recent_results": recent_results,
        "reducing": reducing_results,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })


@app.route("/servers/status")
def servers_status():
    result = {}
    for name, port in [("caliber", 5679), ("mcp", 5002)]:
        try:
            r = requests.get(f"http://localhost:{port}/health", timeout=2)
            d = r.json()
            d["status"] = "online"
            result[name] = d
        except:
            result[name] = {"status": "offline", "port": port}
    return jsonify(result)


@app.route("/loop/status")
def loop_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    INJECT_FLAG  = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    PING_PATH    = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")  # 修正済み
    RAW_DIR      = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    essence_count = 0
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
            essence_count = len(data.get("essence", []))
        except:
            pass
    ping_data = {}
    ping_age = None
    if PING_PATH.exists():
        try:
            text = PING_PATH.read_text(encoding="utf-8")
            ping_data = json.loads(text)
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except:
            pass
    raw_count = len(list(RAW_DIR.glob("*.json"))) if RAW_DIR.exists() else 0
    return jsonify({
        "inject_mode":   inject_mode,
        "essence_count": essence_count,
        "raw_count":     raw_count,
        "ping_latest":   ping_data,
        "ping_age":      ping_age,
    })


@app.route("/loop/inject_toggle", methods=["POST"])
def inject_toggle():
    from pathlib import Path
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    current = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8").strip().upper()
        current = v if v in ["ON","OFF"] else "ON"
    new_mode = "OFF" if current == "ON" else "ON"
    INJECT_FLAG.write_text(new_mode, encoding="utf-8")
    return jsonify({"inject_mode": new_mode})


@app.route("/get_latest_dna")
def get_latest_dna():
    import json
    from pathlib import Path
    PING_PATH = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")  # 修正済み
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    if inject_mode == "OFF":
        return jsonify({"status": "OFF"}), 200
    if not PING_PATH.exists():
        return jsonify({"status": "NO_PING"}), 404
    try:
        ping = json.loads(PING_PATH.read_text(encoding="utf-8"))
        return jsonify({"status": "OK", "ping": ping}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


if __name__ == "__main__":
    print("--- MoCKA STARTING ---")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    ensure_events_csv()
    app.run(host="127.0.0.1", port=5000)


