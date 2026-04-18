import sqlite3
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

# ===== 鬮｢・ｾ繝ｻ・ｪ髯ｷ閧ｴ蝮ｩ・つ繝ｻ・｣鬩搾ｽｯ陞｢・ｼ郢晢ｽｻ鬨ｾ繝ｻ繝ｻ=====
import threading
import time

PILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "storage", "outbox", "PILS")

def auto_process_loop():
    time.sleep(5)
    while True:
        try:
            files = [f for f in os.listdir(PILS_DIR) if f.endswith(".json")]
            if files:
                print("[AUTO] PILS queue: {} -> processing".format(len(files)))
                r = requests.post(
                    CALIBER_SERVER + "/process",
                    json={},
                    headers={"Content-Type": "application/json"},
                    timeout=1800
                )
                if r.status_code == 200:
                    result = r.json()
                    rate = result.get("restore_rate", "?")
                    print("[AUTO] 髯橸ｽｳ陟包ｽ｡繝ｻ・ｺ郢晢ｽｻrestore_rate={}".format(rate))
                else:
                    print("[AUTO] 驛｢・ｧ繝ｻ・ｨ驛｢譎｢・ｽ・ｩ驛｢譎｢・ｽ・ｼ({}): {}".format(r.status_code, r.text[:80]))
            time.sleep(10)
        except Exception as e:
            print("[AUTO] 髣懃§蜚ｱ繝ｻ・､郢晢ｽｻ {}".format(str(e)[:80]))
            time.sleep(30)

_auto_thread = threading.Thread(target=auto_process_loop, daemon=True)
_auto_thread.start()
# ===== 鬮｢・ｾ繝ｻ・ｪ髯ｷ閧ｴ蝮ｩ・つ繝ｻ・｣鬩搾ｽｯ陞｢・ｼ郢晢ｽｻ鬨ｾ繝ｻ繝ｻ繝ｻ繝ｻ・ｸ・ｺ髦ｮ蜷ｮ遨宣し・ｺ繝ｻ・ｧ =====


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
        with open(EVENTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    ensure_events_csv()
    last_n = 0
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8-sig") as f:
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
    with open(master_path, "w", encoding="utf-8-sig") as f:
        json.dump(master_obj, f, ensure_ascii=False, indent=2)
    with open(EVENTS_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def load_history(limit=None):
    ensure_events_csv()
    rows = []
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8-sig") as f:
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
        title = f"髣厄ｽｫ隴取得・ｽ・ｭ郢晢ｽｻ {o}"
        short_summary = "Storage mission dispatched"
    else:
        what_type = "broadcast"
        title = f"髯ｷ闌ｨ・ｽ・ｱ髫ｴ蟶吶・ {o}"
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
        "why_purpose": "save/broadcast from command center",
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
    # 保存(A)の場合はpipelineでessence化
    if c == "A" and memo:
        try:
            _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
            _tx = memo.strip()
            subprocess.Popen([sys.executable, _pl, "--text", _tx, "--no-ping"], cwd=ROOT_DIR)
            print(f"[ASK] pipeline隘搾ｽｷ陷阪・ {_tx[:50]}")
        except Exception as _e:
            print(f"[ASK] pipeline error: {_e}")
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
        with open(EVENTS, encoding="utf-8-sig", errors="replace") as _f:
            rows = list(_csv.reader(_f))
    prev    = _hs.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"
    eid     = f"ECOL_{ts_f}_{source[:4].upper()}"
    h       = _hs.sha256(f"{eid}{ts_str}{text[:100]}{prev}".encode()).hexdigest()[:16]
    rec     = {"event_id":eid,"source":source,"layer":"RAW","url":url,"mode":mode,
               "text":text,"timestamp":ts_str,"hash":h,"prev_hash":prev,"status":"RAW"}
    fname = INFIELD/f"{ts_f}_{eid}.json"
    _json.dump(rec,open(fname,"w",encoding="utf-8-sig"),ensure_ascii=False,indent=2)
    PILS = P(r"C:/Users/sirok/MoCKA/data/storage/outbox/PILS")
    PILS.mkdir(parents=True,exist_ok=True)
    shutil.copy2(fname, PILS/fname.name)
    print(f"[AUTO-PILS] copied to outbox/PILS")
    with open(EVENTS,"a",encoding="utf-8-sig",newline="") as f:
        _csv.writer(f).writerow([eid,ts_str,source,"collect","chat_import","mocka_bridge_v2",
            url[:80],"extension","external","in_operation","normal","A","infield/RAW",
            text[:100].encode("utf-8","replace").decode("utf-8"),prev,"ingest_complete","RAW","local","chat_pipeline","N/A","N/A",
            f"hash={h}|source={source}|mode={mode}"])
    print(f"[COLLECT] {eid} from {source} ({len(text)} chars)")
    # 蜿ｳ繧ｯ繝ｪ繝・け菫晏ｭ倥ｂpipeline縺ｧessence蛹・
    try:
        _pl = os.path.join(ROOT_DIR, 'mocka_pipeline.py')
        subprocess.Popen([sys.executable, _pl, '--text', text[:500], '--no-ping'], cwd=ROOT_DIR)
        print('[COLLECT] pipeline襍ｷ蜍・ ' + eid)
    except Exception as _e:
        print('[COLLECT] pipeline error: ' + str(_e))
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
                d = _json.load(open(os.path.join(re_reduced_dir, f), encoding="utf-8-sig"))
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
                d = _json.load(open(os.path.join(reducing_dir, f), encoding="utf-8-sig"))
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
    ESSENCE_PATH  = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    INJECT_FLAG   = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    PING_PATH     = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    RAW_DIR       = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW")
    RAW_DONE_DIR  = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW_DONE")

    # INJECT MODE
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"

    # ESSENCE COUNT 驕ｯ・ｶ郢晢ｽｻINCIDENT/PHILOSOPHY/OPERATION驍ｵ・ｺ繝ｻ・ｮ髯ｷ蛹ｻ繝ｻ繝ｻ・｡繝ｻ・ｫ髮九ｇ迴ｾ遶擾ｽｩ鬮ｴ繝ｻ・ｽ・ｸ髫ｰ・ｨ繝ｻ・ｰ(髫ｴ蟠｢ﾂ髯樊ｻゑｽｽ・ｧ3)
    essence_count = 0
    essence_axes  = {"INCIDENT": False, "PHILOSOPHY": False, "OPERATION": False}
    essence_updated = None
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8-sig"))
            for axis in essence_axes:
                if data.get(axis) and str(data[axis]).strip():
                    essence_axes[axis] = True
            essence_count = sum(essence_axes.values())
            # 髫ｴ蟠｢ﾂ髫ｴ繝ｻ・ｽ・ｰ驍ｵ・ｺ繝ｻ・ｮ髫ｴ蜴・ｽｽ・ｴ髫ｴ繝ｻ・ｽ・ｰ髫ｴ魃会ｽｽ・･髫ｴ蠑ｱ・・・螳壽╂鬮｢ﾂ繝ｻ・ｾ郢晢ｽｻ
            dates = [data.get(f"{k}_updated") for k in essence_axes if data.get(f"{k}_updated")]
            if dates:
                essence_updated = max(dates)
        except:
            pass

    # RAW / RAW_DONE 驛｢・ｧ繝ｻ・ｫ驛｢・ｧ繝ｻ・ｦ驛｢譎｢・ｽ・ｳ驛｢譏ｴ繝ｻ
    raw_count      = len(list(RAW_DIR.glob("*.json")))      if RAW_DIR.exists()      else 0
    raw_done_count = len(list(RAW_DONE_DIR.glob("*.json"))) if RAW_DONE_DIR.exists() else 0

    # PING
    ping_data = {}
    ping_age  = None
    if PING_PATH.exists():
        try:
            text = PING_PATH.read_text(encoding="utf-8-sig")
            ping_data = json.loads(text)
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except:
            pass

    return jsonify({
        "inject_mode":     inject_mode,
        "essence_count":   essence_count,       # 0-3: 髯ｷ蛹ｻ繝ｻ繝ｻ・｡繝ｻ・ｫ髮九ｇ迴ｾ遶擾ｽｩ鬮ｴ繝ｻ・ｽ・ｸ髫ｰ・ｨ繝ｻ・ｰ
        "essence_axes":    essence_axes,         # {INCIDENT:bool, PHILOSOPHY:bool, OPERATION:bool}
        "essence_updated": essence_updated,      # 髫ｴ蟠｢ﾂ鬩搾ｽｨ郢ｧ莠･・ｳ・ｩ髫ｴ繝ｻ・ｽ・ｰ髫ｴ魃会ｽｽ・･髫ｴ蠑ｱ繝ｻ
        "raw_count":       raw_count,            # 髫ｴ蟷｢・ｽ・ｪ髯ｷ繝ｻ・ｽ・ｦ鬨ｾ繝ｻ繝ｻAW髣比ｼ夲ｽｽ・ｶ髫ｰ・ｨ繝ｻ・ｰ
        "raw_done_count":  raw_done_count,       # 髯ｷ繝ｻ・ｽ・ｦ鬨ｾ繝ｻ繝ｻ繝ｻ・ｸ陋ｹ・ｻ遶擾ｽｩRAW髣比ｼ夲ｽｽ・ｶ髫ｰ・ｨ繝ｻ・ｰ
        "ping_latest":     ping_data,
        "ping_age":        ping_age,
    })


@app.route("/loop/inject_toggle", methods=["POST"])
def inject_toggle():
    from pathlib import Path
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    current = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        current = v if v in ["ON","OFF"] else "ON"
    new_mode = "OFF" if current == "ON" else "ON"
    INJECT_FLAG.write_text(new_mode, encoding="utf-8-sig")
    return jsonify({"inject_mode": new_mode})


@app.route("/get_latest_dna")
def get_latest_dna():
    import json
    from pathlib import Path
    PING_PATH = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    if inject_mode == "OFF":
        return jsonify({"status": "OFF"}), 200
    if not PING_PATH.exists():
        return jsonify({"status": "NO_PING"}), 404
    try:
        ping = json.loads(PING_PATH.read_text(encoding="utf-8-sig"))
        return jsonify({"status": "OK", "ping": ping}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/ngrok/status')
def ngrok_status():
    import requests as req
    try:
        r = req.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        d = r.json()
        t = d['tunnels'][0] if d.get('tunnels') else None
        return json.dumps({
            'status': 'online' if t else 'offline',
            'public_url': t['public_url'] if t else '',
            'addr': t['config']['addr'] if t else ''
        }), 200, {'Content-Type': 'application/json'}
    except:
        return json.dumps({'status': 'offline', 'public_url': '', 'addr': ''}), 200, {'Content-Type': 'application/json'}



@app.route("/pipeline/status")
def pipeline_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH  = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    PATTERNS_FILE = Path(r"C:\Users\sirok\MoCKA\interface\danger_patterns.json")
    LEARN_LOG     = Path(r"C:\Users\sirok\MoCKA\data\language_learn_log.json")
    PING_PATH     = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    WATCHDOG_LOG  = Path(r"C:\Users\sirok\MoCKA\data\watchdog_processed.json")
    result = {}
    input_info = {"chrome_extension":{"last":None},"watchdog":{"running":False},"pipeline":{"last":None}}
    if WATCHDOG_LOG.exists():
        try:
            wd = json.loads(WATCHDOG_LOG.read_text(encoding="utf-8"))
            input_info["watchdog"]["running"] = True
            input_info["watchdog"]["processed_count"] = len(wd)
        except: pass
    if PING_PATH.exists():
        try:
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            input_info["pipeline"]["last"] = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass
    result["input"] = input_info
    layers = {}
    base = Path(r"C:\Users\sirok\MoCKA\data\storage")
    for layer in ["RAW","REDUCED","RE_REDUCED","REDUCING","CORE","ESSENCE","RAW_DONE"]:
        d = base / "infield" / layer
        layers[layer] = len(list(d.glob("*.json"))) if d.exists() else 0
    pils = base / "outbox" / "PILS"
    layers["PILS"] = len(list(pils.glob("*.json"))) if pils.exists() else 0
    result["layers"] = layers
    danger_info = {"total":0,"tier1":0,"tier2":0,"tier3":0,"escalation":0,"silent_danger":0,"learned_today":0,"last_critical":None}
    if PATTERNS_FILE.exists():
        try:
            p = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
            for tier in ["tier1","tier2","tier3","escalation","silent_danger"]:
                n = len(p.get(tier,{}).get("patterns",[]))
                danger_info[tier] = n
                danger_info["total"] += n
        except: pass
    if LEARN_LOG.exists():
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            learned = 0; last_critical = None
            with open(LEARN_LOG, encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp","").startswith(today):
                            learned += entry.get("added_count", 0)
                        if entry.get("level") in ("CRITICAL","DANGER"):
                            last_critical = entry.get("incident_id")
                    except: pass
            danger_info["learned_today"] = learned
            danger_info["last_critical"] = last_critical
        except: pass
    result["danger"] = danger_info
    essence_detail = {}
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
            for axis in ["INCIDENT","PHILOSOPHY","OPERATION"]:
                text = data.get(axis,"")
                essence_detail[axis] = {"text":text[:120] if text else "","updated":data.get(f"{axis}_updated",""),"count":data.get(f"{axis}_source_count",0),"filled":bool(text and text.strip())}
        except: pass
    result["essence"] = essence_detail
    return jsonify(result)

@app.route("/essence/detail")
def essence_detail():
    import json
    from pathlib import Path
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    if not ESSENCE_PATH.exists():
        return jsonify({"status":"NOT_FOUND"})
    try:
        return jsonify({"status":"OK","data":json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))})
    except Exception as e:
        return jsonify({"status":"ERROR","message":str(e)})

@app.route("/danger/status")
def danger_status():
    import json
    from pathlib import Path
    PATTERNS_FILE = Path(r"C:\Users\sirok\MoCKA\interface\danger_patterns.json")
    if not PATTERNS_FILE.exists():
        return jsonify({"status":"NOT_FOUND"})
    try:
        p = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
        summary = {}
        for tier in ["tier1","tier2","tier3","escalation","silent_danger"]:
            patterns = p.get(tier,{}).get("patterns",[])
            summary[tier] = {"count":len(patterns),"samples":patterns[:3]}
        return jsonify({"status":"OK","summary":summary,"meta":p.get("_meta",{})})
    except Exception as e:
        return jsonify({"status":"ERROR","message":str(e)})

# ============================================================
# MoCKA Public API — 全AI向け公開エンドポイント
# ngrok経由で任命済みAIが全サービスにアクセス可能
# ============================================================

@app.route("/public/todo")
def public_todo():
    """MOCKA_TODO.json を全AI向けに公開"""
    import json
    from pathlib import Path
    TODO_PATH = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    if not TODO_PATH.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(TODO_PATH.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/overview")
def public_overview():
    """MOCKA_OVERVIEW.json を全AI向けに公開"""
    import json
    from pathlib import Path
    OV_PATH = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")
    if not OV_PATH.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(OV_PATH.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/essence")
def public_essence():
    """lever_essence.json を全AI向けに公開"""
    import json
    from pathlib import Path
    EP = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    if not EP.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(EP.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/events")
def public_events():
    """直近イベントを全AI向けに公開"""
    import csv as _csv
    from pathlib import Path
    EP = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
    n = int(request.args.get("n", 20))
    if not EP.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        rows = []
        with open(EP, encoding="utf-8-sig", errors="replace") as f:
            reader = _csv.DictReader(f)
            for r in reader:
                rows.append({k: (v or "") for k, v in r.items()})
        return jsonify({"count": len(rows), "events": rows[-n:]})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/write_event", methods=["POST"])
def public_write_event():
    """全AI向けイベント記録エンドポイント"""
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title", "")
    description = payload.get("description", "")
    author = payload.get("author", "external_ai")
    tags = payload.get("tags", "")
    if not title or not description:
        return jsonify({"status": "error", "message": "title and description required"}), 400
    meta = {
        "what_type": "ai_event",
        "category_ab": "A",
        "target_class": "infield",
        "title": title,
        "short_summary": description[:200],
        "who_actor": author,
        "where_component": "public_api",
        "where_path": "/public/write_event",
        "why_purpose": tags,
        "how_trigger": "external_ai_call",
        "channel_type": "http_api",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "before_state": "N/A",
        "after_state": "N/A",
        "change_type": "N/A",
        "impact_scope": "local",
        "impact_result": "N/A",
        "related_event_id": "N/A",
        "trace_id": "N/A",
        "free_note": description,
    }
    append_event(meta)
    return jsonify({"status": "ok", "event_id": next_event_id()})

@app.route("/public/pipeline", methods=["POST"])
def public_pipeline():
    """全AI向けpipeline実行エンドポイント（essenceへの直接投入）"""
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text", "").strip()
    author = payload.get("author", "external_ai")
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    try:
        _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
        subprocess.Popen([sys.executable, _pl, "--text", text[:1000], "--no-ping"], cwd=ROOT_DIR)
        print("[PUBLIC_PIPELINE] {} -> pipeline: {}...".format(author, text[:50]))
        return jsonify({"status": "ok", "message": "pipeline started", "author": author})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/public/seal", methods=["POST"])
def public_seal():
    """全AI向けsealエンドポイント（events.csvのSHA-256）"""
    import hashlib
    from pathlib import Path
    EP = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
    if not EP.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        h = hashlib.sha256(EP.read_bytes()).hexdigest()
        return jsonify({"status": "ok", "sha256": h, "file": str(EP), "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/status")
def public_status():
    """MoCKA全体の状態を一括返却 — 新規AIのオンボーディング用"""
    import json as _j
    from pathlib import Path
    result = {
        "system": "MoCKA v3.0",
        "status": "online",
        "services": {
            "todo":      "/public/todo",
            "overview":  "/public/overview",
            "essence":   "/public/essence",
            "events":    "/public/events?n=20",
            "write_event": "/public/write_event (POST)",
            "pipeline":  "/public/pipeline (POST)",
            "seal":      "/public/seal (POST)",
            "pipeline_status": "/pipeline/status",
            "danger_status":   "/danger/status",
            "essence_detail":  "/essence/detail",
        },
        "mcp": {
            "url": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp",
            "tools": ["mocka_get_todo","mocka_get_overview","mocka_get_essence",
                      "mocka_write_event","mocka_list_events","mocka_seal","mocka_search","mocka_read_event"]
        },
        "ngrok": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev",
        "appointed_ai": ["Claude","Gemini","GPT","Copilot","Perplexity"],
    }
    return jsonify(result)
if __name__ == "__main__":
    print("--- MoCKA STARTING ---")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    ensure_events_csv()
    app.run(host="127.0.0.1", port=5000)
