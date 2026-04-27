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

# --- Pattern Engine v2 ---
try:
    from interface.pattern_engine_v2 import PatternEngine as _PatternEngine
    _pattern_engine = _PatternEngine()
    print(f"[pattern_engine] OK - {len(_pattern_engine.registry.records)} keywords")
except Exception as _pe_err:
    _pattern_engine = None
    print(f"[pattern_engine] WARN: {_pe_err}")
_pattern_score_history = []
_PATTERN_HISTORY_MAX   = 100

def run_pattern_score(text):
    global _pattern_score_history
    if not _pattern_engine or not text:
        return
    try:
        r = _pattern_engine.analyze(text)
        r["timestamp"] = datetime.now().isoformat()
        r["preview"]   = text[:60]
        _pattern_score_history.append(r)
        if len(_pattern_score_history) > _PATTERN_HISTORY_MAX:
            _pattern_score_history = _pattern_score_history[-_PATTERN_HISTORY_MAX:]
        if r["verdict"] in ("CRITICAL","DANGER"):
            print(f"[pattern] {r['verdict']} R={r['R']} '{text[:40]}'")
    except Exception as e:
        print(f"[pattern_engine] error: {e}")

from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# ===== 自動処理ループ（PILSキュー監視） =====
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
                    print("[AUTO] 完了 restore_rate={}".format(rate))
                else:
                    print("[AUTO] エラー({}): {}".format(r.status_code, r.text[:80]))
            time.sleep(10)
        except Exception as e:
            print("[AUTO] 例外: {}".format(str(e)[:80]))
            time.sleep(30)

_auto_thread = threading.Thread(target=auto_process_loop, daemon=True)
_auto_thread.start()

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
PATTERN_SCORE  = os.path.join(DATA_DIR, "latest_score.json")

FIELDNAMES = [
    "event_id", "when", "who_actor", "what_type",
    "where_component", "where_path", "why_purpose", "how_trigger",
    "channel_type", "lifecycle_phase", "risk_level",
    "category_ab", "target_class", "title", "short_summary",
    "before_state", "after_state", "change_type",
    "impact_scope", "impact_result", "related_event_id", "trace_id", "free_note",
]

_intent_queue = {}
_intent_lock = threading.Lock()

# ===== Pattern Hook =====
def run_pattern_score(text):
    try:
        import pattern_engine
        result = pattern_engine.score_text(text)
        print(f"[PATTERN] verdict={result['verdict']} s={result['success_score']} f={result['failure_score']}")
        with open(PATTERN_SCORE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result
    except Exception as e:
        print(f"[PATTERN] error: {e}")
        return None

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

@app.route("/get_intent/<ai_name>")
def get_intent(ai_name):
    with _intent_lock:
        queue = _intent_queue.get(ai_name, [])
        if not queue:
            return '', 204
        payload = queue.pop(0)
        _intent_queue[ai_name] = queue
    print(f"[INTENT] {ai_name} -> payload dispatched")
    return jsonify({"payload": payload})

@app.route("/set_intent", methods=["POST"])
def set_intent():
    payload = request.get_json(force=True, silent=True) or {}
    ai_name = payload.get("ai_name", "")
    text    = payload.get("text", "")
    if not ai_name or not text:
        return jsonify({"status": "error", "message": "ai_name and text required"}), 400
    with _intent_lock:
        if ai_name not in _intent_queue:
            _intent_queue[ai_name] = []
        _intent_queue[ai_name].append(text)
    append_event({
        "what_type": "collaboration",
        "category_ab": "B",
        "target_class": ai_name,
        "title": f"協業依頼 -> {ai_name}",
        "short_summary": text[:100],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "local",
    })
    return jsonify({"status": "ok", "ai_name": ai_name})

@app.route("/collaborate", methods=["POST"])
def collaborate():
    payload = request.get_json(force=True, silent=True) or {}
    text    = payload.get("text", payload.get("prompt", ""))
    targets = payload.get("targets", ["ChatGPT", "Gemini", "Claude", "Perplexity", "Copilot", "Genspark"])
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    with _intent_lock:
        for ai_name in targets:
            if ai_name not in _intent_queue:
                _intent_queue[ai_name] = []
            _intent_queue[ai_name].append(text)
    try:
        subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", text, "collaborate"], cwd=ROOT_DIR)
    except Exception as e:
        print(f"[COLLABORATE] orchestra error: {e}")
    append_event({
        "what_type": "collaboration",
        "category_ab": "B",
        "target_class": ",".join(targets),
        "title": f"協業一括投入: {text[:40]}",
        "short_summary": text[:200],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "multi_ai",
    })
    return jsonify({"status": "ok", "targets": targets})

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
        r = requests.post(CALIBER_SERVER + "/process", json={}, headers={"Content-Type": "application/json"}, timeout=1800)
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
    subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", prompt, mode], cwd=ROOT_DIR)
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
        title = f"保存取得 {o}"
        short_summary = "Storage mission dispatched"
    else:
        what_type = "broadcast"
        title = f"共有配信 {o}"
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
    if c == "A" and memo:
        try:
            _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
            subprocess.Popen([sys.executable, _pl, "--text", memo.strip(), "--no-ping"], cwd=ROOT_DIR)
        except Exception as _e:
            print(f"[ASK] pipeline error: {_e}")
        # Pattern scoring
        threading.Thread(target=run_pattern_score, args=(memo,), daemon=True).start()
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
    with open(EVENTS,"a",encoding="utf-8-sig",newline="") as f:
        _csv.writer(f).writerow([eid,ts_str,source,"collect","chat_import","mocka_bridge_v2",
            url[:80],"extension","external","in_operation","normal","A","infield/RAW",
            text[:100].encode("utf-8","replace").decode("utf-8"),prev,"ingest_complete","RAW","local","chat_pipeline","N/A","N/A",
            f"hash={h}|source={source}|mode={mode}"])
    try:
        _pl = os.path.join(ROOT_DIR, 'mocka_pipeline.py')
        subprocess.Popen([sys.executable, _pl, '--text', text[:500], '--no-ping'], cwd=ROOT_DIR)
    except Exception as _e:
        print('[COLLECT] pipeline error: ' + str(_e))
    # Pattern scoring
    threading.Thread(target=run_pattern_score, args=(text[:500],), daemon=True).start()
    return jsonify({"status":"ok","event_id":eid,"hash":h})

# ===== Success Pattern API =====
SUCCESS_PATTERNS_FILE = os.path.join(DATA_DIR, "success_patterns.json")

def load_success_patterns():
    if not os.path.exists(SUCCESS_PATTERNS_FILE):
        return {"hint": [], "great": []}
    with open(SUCCESS_PATTERNS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_success_patterns(patterns):
    with open(SUCCESS_PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

@app.route("/success", methods=["POST"])
def success():
    payload = request.get_json(force=True, silent=True) or {}
    success_type = payload.get("type", "hint")
    text   = payload.get("text", "").strip()
    source = payload.get("source", "unknown")
    url    = payload.get("url", "")
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    patterns = load_success_patterns()
    entry = {"text": text, "source": source, "url": url, "timestamp": datetime.now().isoformat(timespec="seconds")}
    patterns.setdefault(success_type, []).append(entry)
    save_success_patterns(patterns)
    what_type = "success_hint" if success_type == "hint" else "success_great"
    label     = "[hint]" if success_type == "hint" else "[great]"
    append_event({
        "what_type": what_type,
        "category_ab": "A",
        "target_class": "infield",
        "title": f"{label} {text[:40]}",
        "short_summary": text[:200],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "where_path": "mocka-extension/background.js",
        "why_purpose": f"成功シグナル収集: {success_type}",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "local",
        "free_note": f"source={source}|type={success_type}",
    })
    try:
        _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
        subprocess.Popen([sys.executable, _pl, "--text", f"{label} {text[:500]}", "--no-ping"], cwd=ROOT_DIR)
    except Exception as e:
        print(f"[SUCCESS] pipeline error: {e}")
    # Pattern scoring
    threading.Thread(target=run_pattern_score, args=(text,), daemon=True).start()
    print(f"[SUCCESS] {what_type}: {text[:50]}")
    return jsonify({"status": "ok", "type": success_type, "stored": len(patterns.get(success_type, []))})

@app.route("/success/patterns")
def success_patterns():
    patterns = load_success_patterns()
    return jsonify({
        "hint_count":  len(patterns.get("hint", [])),
        "great_count": len(patterns.get("great", [])),
        "hints":  patterns.get("hint", [])[-10:],
        "greats": patterns.get("great", [])[-10:],
    })

@app.route("/pattern/score")
def pattern_score():
    if not os.path.exists(PATTERN_SCORE):
        return jsonify({"status": "NO_DATA"})
    try:
        with open(PATTERN_SCORE, encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

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
                recent_results.append({"file": f, "source": d.get("source",""), "restore_rate": d.get("restore_rate", 0), "timestamp": d.get("timestamp",""), "status": d.get("status",""), "preview": d.get("extraction","")[:100]})
            except: pass
    try:
        r = __import__('requests').get("http://localhost:5679/health", timeout=2)
        server = "online"
    except:
        server = "offline"
    return __import__('flask').jsonify({"layers": counts, "caliber_server": server, "queue": pils_files, "recent_results": recent_results, "timestamp": datetime.now().strftime("%H:%M:%S")})

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
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
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
            dates = [data.get(f"{k}_updated") for k in essence_axes if data.get(f"{k}_updated")]
            if dates:
                essence_updated = max(dates)
        except: pass
    raw_count      = len(list(RAW_DIR.glob("*.json")))      if RAW_DIR.exists()      else 0
    raw_done_count = len(list(RAW_DONE_DIR.glob("*.json"))) if RAW_DONE_DIR.exists() else 0
    ping_data = {}
    ping_age  = None
    if PING_PATH.exists():
        try:
            text = PING_PATH.read_text(encoding="utf-8-sig")
            ping_data = json.loads(text)
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass
    # --- 8ステージ実データ収集 ---
    EVENTS_CSV   = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
    RECURRENCE_CSV = Path(r"C:\Users\sirok\MoCKA\data\recurrence_registry.csv")
    PREVENTION_JSON = Path(r"C:\Users\sirok\MoCKA\data\prevention_queue.json")
    LEDGER_JSON  = Path(r"C:\Users\sirok\MoCKA\runtime\main\ledger.json")

    # ② Record: events.csv総件数
    record_count = 0
    # ③ Incident件数
    incident_count = 0
    # ⑥ Decision件数
    decision_count = 0
    # ⑦ Action件数
    action_count = 0
    if EVENTS_CSV.exists():
        try:
            import csv
            with open(EVENTS_CSV, encoding="utf-8-sig", errors="replace") as f:
                rows = list(csv.DictReader(f))
            record_count = len(rows)
            for r in rows:
                wt = str(r.get("what_type","")).upper()
                rl = str(r.get("risk_level","")).upper()
                title = str(r.get("title","")).upper()
                if rl in ["DANGER","CRITICAL"] or "INCIDENT" in wt or "INCIDENT" in title:
                    incident_count += 1
                if "DECISION_APPROVED" in wt or "DECISION_APPROVED" in title:
                    decision_count += 1
                if "AUTO_GATE_APPROVED" in wt or "AUTO_GATE" in title:
                    action_count += 1
        except: pass

    # ④ Recurrence件数
    recurrence_count = 0
    if RECURRENCE_CSV.exists():
        try:
            import csv as _csv
            with open(RECURRENCE_CSV, encoding="utf-8-sig", errors="replace") as f:
                recurrence_count = sum(1 for _ in _csv.DictReader(f))
        except: pass

    # ⑤ Prevention未承認件数
    prevention_pending = 0
    if PREVENTION_JSON.exists():
        try:
            pdata = json.loads(PREVENTION_JSON.read_text(encoding="utf-8-sig"))
            items = pdata if isinstance(pdata, list) else pdata.get("queue", [])
            prevention_pending = sum(1 for x in items if str(x.get("status","")).upper() not in ["APPROVED","REJECTED"])
        except: pass

    # ⑧ Audit: 最終seal時刻
    last_seal = None
    last_seal_hash = None
    if LEDGER_JSON.exists():
        try:
            ldata = json.loads(LEDGER_JSON.read_text(encoding="utf-8-sig"))
            last_seal = ldata.get("last_updated") or ldata.get("timestamp")
            last_seal_hash = ldata.get("hash") or ldata.get("anchor_hash")
        except: pass

    civilization_loop = {
        "observe":    {"label": "Observe",    "count": raw_count,          "detail": "RAW未処理"},
        "record":     {"label": "Record",     "count": record_count,       "detail": "events.csv総件数"},
        "incident":   {"label": "Incident",   "count": incident_count,     "detail": "DANGER/CRITICAL/INCIDENT"},
        "recurrence": {"label": "Recurrence", "count": recurrence_count,   "detail": "再発パターン"},
        "prevention": {"label": "Prevention", "count": prevention_pending,  "detail": "未承認Prevention案"},
        "decision":   {"label": "Decision",   "count": decision_count,     "detail": "承認済みDecision"},
        "action":     {"label": "Action",     "count": action_count,       "detail": "Auto Gate実行"},
        "audit":      {"label": "Audit",      "last_seal": last_seal,      "last_seal_hash": last_seal_hash},
    }

    return jsonify({"inject_mode": inject_mode, "essence_count": essence_count, "essence_axes": essence_axes,
                    "essence_updated": essence_updated, "raw_count": raw_count, "raw_done_count": raw_done_count,
                    "ping_latest": ping_data, "ping_age": ping_age,
                    "civilization_loop": civilization_loop})

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
    from pathlib import Path
    PING_PATH   = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    TODO_PATH   = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    if inject_mode == "OFF":
        return jsonify({"status": "OFF"}), 200
    if not PING_PATH.exists():
        return jsonify({"status": "NO_PING"}), 404
    todo_summary = []
    try:
        todo_data = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
        priority_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
        pending = [t for t in todo_data.get("todos", []) if t.get("status") == "未着手"]
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 9))
        todo_summary = [{"id": t.get("id"), "title": t.get("title"), "priority": t.get("priority")} for t in pending[:5]]
    except: todo_summary = []
    try:
        ping = json.loads(PING_PATH.read_text(encoding="utf-8-sig"))
        return jsonify({"status": "OK", "ping": ping, "todo_summary": todo_summary}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route("/gemini/briefing")
def gemini_briefing():
    from pathlib import Path
    TODO_PATH    = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    todos_pending = []
    try:
        todo_data = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
        priority_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
        pending = [t for t in todo_data.get("todos", []) if t.get("status") == "未着手"]
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 9))
        todos_pending = [{"id": t.get("id"), "title": t.get("title"), "priority": t.get("priority")} for t in pending]
    except: pass
    essence = {}
    try:
        essence = json.loads(ESSENCE_PATH.read_text(encoding="utf-8-sig"))
    except: pass
    top = todos_pending[0] if todos_pending else {}
    header = f"[MoCKA SESSION START]\nPhase 2進行中\n未着手TODO: {len(todos_pending)}件\n最重要: {top.get('id','')} {top.get('title','')}"
    return jsonify({"status": "OK", "prompt_header": header, "todos_pending": todos_pending, "essence": essence}), 200

@app.route("/report", methods=["POST"])
def receive_report():
    from pathlib import Path
    REPORT_DIR = Path(r"C:\Users\sirok\MoCKA\data\reports")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        data = request.get_json(force=True)
        data["received_at"] = datetime.now().isoformat()
        fname = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        (REPORT_DIR / fname).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"status": "OK", "saved": fname}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/ngrok/status')
def ngrok_status():
    import requests as req
    try:
        r = req.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        d = r.json()
        t = d['tunnels'][0] if d.get('tunnels') else None
        return json.dumps({'status': 'online' if t else 'offline', 'public_url': t['public_url'] if t else '', 'addr': t['config']['addr'] if t else ''}), 200, {'Content-Type': 'application/json'}
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

@app.route("/public/todo")
def public_todo():
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
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title", "")
    description = payload.get("description", "")
    author = payload.get("author", "external_ai")
    tags = payload.get("tags", "")
    if not title or not description:
        return jsonify({"status": "error", "message": "title and description required"}), 400
    meta = {
        "what_type": "ai_event", "category_ab": "A", "target_class": "infield",
        "title": title, "short_summary": description[:200], "who_actor": author,
        "where_component": "public_api", "where_path": "/public/write_event",
        "why_purpose": tags, "how_trigger": "external_ai_call",
        "channel_type": "http_api", "lifecycle_phase": "in_operation",
        "risk_level": "normal", "before_state": "N/A", "after_state": "N/A",
        "change_type": "N/A", "impact_scope": "local", "impact_result": "N/A",
        "related_event_id": "N/A", "trace_id": "N/A", "free_note": description,
    }
    append_event(meta)
    return jsonify({"status": "ok", "event_id": next_event_id()})

@app.route("/public/pipeline", methods=["POST"])
def public_pipeline():
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text", "").strip()
    author = payload.get("author", "external_ai")
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    try:
        _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
        subprocess.Popen([sys.executable, _pl, "--text", text[:1000], "--no-ping"], cwd=ROOT_DIR)
        return jsonify({"status": "ok", "message": "pipeline started", "author": author})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/public/seal", methods=["POST"])
def public_seal():
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
    result = {
        "system": "MoCKA v3.0",
        "status": "online",
        "services": {
            "todo": "/public/todo", "overview": "/public/overview",
            "essence": "/public/essence", "events": "/public/events?n=20",
            "write_event": "/public/write_event (POST)", "pipeline": "/public/pipeline (POST)",
            "seal": "/public/seal (POST)", "pipeline_status": "/pipeline/status",
            "danger_status": "/danger/status", "essence_detail": "/essence/detail",
            "collaborate": "/collaborate (POST)", "set_intent": "/set_intent (POST)",
            "get_intent": "/get_intent/<ai_name> (GET)",
            "pattern_score": "/pattern/score (GET)",
        },
        "mcp": {"url": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp"},
        "ngrok": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev",
        "appointed_ai": ["Claude","Gemini","GPT","Copilot","Perplexity"],
    }
    return jsonify(result)

@app.route('/pattern/status')
def pattern_status():
    if _pattern_engine is None:
        return jsonify({"status": "unavailable"})
    reg     = _pattern_engine.registry
    recent  = _pattern_score_history[-20:]
    d_count = sum(1 for r in recent if r["verdict"] in ("DANGER","CRITICAL"))
    s_count = sum(1 for r in recent if r["verdict"] == "SUCCESS")
    return jsonify({
        "status":         "ok",
        "total_keywords": len(reg.records),
        "danger_kw":      len(reg.danger_keywords()),
        "success_kw":     len(reg.success_keywords()),
        "recent_count":   len(recent),
        "danger_count":   d_count,
        "success_count":  s_count,
        "last_verdict":   recent[-1]["verdict"] if recent else "NEUTRAL",
        "last_R":         recent[-1]["R"]       if recent else 0.0,
        "history":        recent[-10:],
    })
# ============================================================

# ============================================================
# 全自動LOOP: DANGER検知 → essence直結パイプ
# ============================================================
import threading as _lt, time as _lt2

def _auto_danger_to_essence(incident_text: str):
    """DANGER/CRITICAL検知時にessenceへ直接記録する"""
    try:
        from pathlib import Path as _P
        import json as _j
        essence_path = _P(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
        if not essence_path.exists():
            return
        data = _j.loads(essence_path.read_text(encoding="utf-8"))
        current = data.get("INCIDENT", "")
        data["INCIDENT"] = f"【自動記録】{incident_text[:60]} | {current[:60]}"
        data["INCIDENT_updated"] = datetime.now().isoformat()
        essence_path.write_text(_j.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # ping_generator自動実行
        import subprocess
        ping_gen = __import__("pathlib").Path(str(ROOT_DIR)) / "interface" / "ping_generator.py"
        if ping_gen.exists():
            subprocess.Popen(["python", str(ping_gen)], cwd=str(ROOT_DIR))
        print(f"[AUTO-PIPE] essence更新: {incident_text[:40]}")
    except Exception as e:
        print(f"[AUTO-PIPE] エラー: {e}")

# ============================================================
# 全自動LOOP: Audit（日次seal + 50件トリガー）
# ============================================================
_last_seal_date = [None]
_last_event_count = [0]

def auto_audit_loop():
    import subprocess, time
    print("[AUTO-AUDIT] 日次自動sealループ開始")
    while True:
        try:
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            if now.hour == 0 and _last_seal_date[0] != today:
                seal_script = __import__("pathlib").Path(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
                if seal_script.exists():
                    subprocess.run(["python", str(seal_script), "AUTO_SEAL_" + today],
                                   cwd=str(ROOT_DIR), timeout=30)
                    print(f"[AUTO-AUDIT] 日次seal完了")
                _last_seal_date[0] = today
            events_path = __import__("pathlib").Path(str(ROOT_DIR)) / "data" / "events.csv"
            if events_path.exists():
                with open(events_path, encoding="utf-8") as f:
                    count = sum(1 for _ in f)
                if count - _last_event_count[0] >= 50:
                    seal_script = __import__("pathlib").Path(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
                    if seal_script.exists():
                        subprocess.run(["python", str(seal_script), "AUTO_SEAL_50EVT"],
                                       cwd=str(ROOT_DIR), timeout=30)
                        print(f"[AUTO-AUDIT] 50件seal完了")
                    _last_event_count[0] = count
        except Exception as e:
            print(f"[AUTO-AUDIT] ループ例外: {e}")
        _lt2.sleep(60)

_audit_thread = _lt.Thread(target=auto_audit_loop, daemon=True)
_audit_thread.start()


@app.route("/audit/status")
def audit_status():
    from pathlib import Path as _P
    seal_log = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    log = {}
    if seal_log.exists():
        try:
            log = __import__("json").loads(seal_log.read_text(encoding="utf-8"))
        except: pass
    return jsonify({"last_seal": log, "seal_log_exists": seal_log.exists()})

@app.route("/audit/seal", methods=["POST"])
def audit_seal_manual():
    import subprocess
    from pathlib import Path as _P
    seal_script = _P(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
    seal_log    = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    if seal_script.exists():
        result = subprocess.run(
            ["python", str(seal_script), "MANUAL_SEAL_" + datetime.now().strftime("%Y%m%d_%H%M%S")],
            cwd=str(ROOT_DIR), capture_output=True, text=True, timeout=30
        )
        log = {"sealed_at": datetime.now().isoformat(), "result": result.stdout[:200]}
        seal_log.write_text(__import__("json").dumps(log, ensure_ascii=False), encoding="utf-8")
        return jsonify({"status": "ok", "sealed_at": log["sealed_at"]})
    return jsonify({"status": "error", "message": "seal script not found"})


# ============================================================
# AUTO-CHAIN: append_event後のessence自動トリガー
# ============================================================
import threading as _chain_t

def _trigger_essence_chain(row):
    def _run():
        try:
            from pathlib import Path as _P
            import subprocess as _sp
            risk = row.get("risk_level","normal").lower()
            wtype = row.get("what_type","").lower()
            trigger_types = {"danger","critical","incident","claim","prevention"}
            if risk not in ("danger","critical") and wtype not in trigger_types:
                return
            ec = _P(ROOT_DIR) / "interface" / "essence_classifier.py"
            pg = _P(ROOT_DIR) / "interface" / "ping_generator.py"
            if ec.exists():
                _sp.run(["python", str(ec)], cwd=ROOT_DIR, timeout=30)
            if pg.exists():
                _sp.run(["python", str(pg)], cwd=ROOT_DIR, timeout=30)
            print("[AUTO-CHAIN] essence更新: " + row.get("event_id","?"))
        except Exception as e:
            print("[AUTO-CHAIN] エラー: " + str(e))
    _chain_t.Thread(target=_run, daemon=True).start()

# ============================================================
# PREVENTION QUEUE + DECISION
# ============================================================
from pathlib import Path as _pp
PREVENTION_QUEUE_PATH = _pp(ROOT_DIR) / "data" / "prevention_queue.json"

def _load_pqueue():
    if PREVENTION_QUEUE_PATH.exists():
        try:
            return json.loads(PREVENTION_QUEUE_PATH.read_text(encoding="utf-8"))
        except:
            pass
    return {"queue": []}

def _save_pqueue(data):
    PREVENTION_QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

@app.route("/prevention/queue")
def prevention_queue():
    data = _load_pqueue()
    pending = [q for q in data.get("queue", []) if q.get("status") == "pending"]
    return jsonify({"queue": data.get("queue", []), "pending_count": len(pending)})

@app.route("/decision/approve", methods=["POST"])
def decision_approve():
    payload = request.get_json(force=True, silent=True) or {}
    pid = payload.get("id", "")
    data = _load_pqueue()
    approved = None
    for item in data["queue"]:
        if item.get("id") == pid and item.get("status") == "pending":
            item["status"] = "approved"
            item["approved_at"] = datetime.now().isoformat()
            approved = item
            break
    if not approved:
        return jsonify({"status": "not_found"}), 404
    _save_pqueue(data)
    append_event({
        "what_type": "DECISION_APPROVED",
        "title": "[承認] " + approved.get("title", ""),
        "short_summary": approved.get("description", "")[:100],
        "risk_level": approved.get("risk_level", "normal"),
        "who_actor": "kimura_hakase",
        "free_note": pid,
    })
    def _upd():
        try:
            from pathlib import Path as _P
            import subprocess as _sp
            pg = _P(ROOT_DIR) / "interface" / "ping_generator.py"
            if pg.exists():
                _sp.run(["python", str(pg)], cwd=ROOT_DIR, timeout=30)
        except Exception as e:
            print("[ACTION] " + str(e))
    _chain_t.Thread(target=_upd, daemon=True).start()
    return jsonify({"status": "ok", "approved": pid})

@app.route("/decision/reject", methods=["POST"])
def decision_reject():
    payload = request.get_json(force=True, silent=True) or {}
    pid = payload.get("id", "")
    data = _load_pqueue()
    for item in data["queue"]:
        if item.get("id") == pid and item.get("status") == "pending":
            item["status"] = "rejected"
            item["rejected_at"] = datetime.now().isoformat()
            break
    _save_pqueue(data)
    append_event({
        "what_type": "DECISION_REJECTED",
        "title": "[却下] " + pid,
        "short_summary": "Human Gateで却下",
        "risk_level": "normal",
        "who_actor": "kimura_hakase",
        "free_note": pid,
    })
    return jsonify({"status": "ok", "rejected": pid})


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'port': 5000})

if __name__ == "__main__":
    print("--- MoCKA STARTING ---")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    ensure_events_csv()
    app.run(host="127.0.0.1", port=5000)







