import csv
import os
import json
import subprocess
import sys
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
EVENTS_CSV = os.path.join(DATA_DIR, "events.csv")

BASE_DIR = ROOT_DIR
RECORDS_DIR = os.path.join(BASE_DIR, "records")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OLD_DIR = os.path.join(BASE_DIR, "OLD_FILES")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

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
    name = row.get("title", "N/A")
    summary = row.get("short_summary", "N/A")
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


@app.route("/orchestra", methods=["POST"])
def orchestra():
    payload = request.get_json(force=True, silent=True) or {}
    prompt = payload.get("prompt", "MoCKA Broadcast")
    mode = payload.get("mode", "orchestra")
    # router.py経由で統一
    sys.path.insert(0, os.path.join(ROOT_DIR, "interface"))
    from router import MoCKARouter
    router = MoCKARouter()
    if mode == "orchestra":
        subprocess.Popen([sys.executable, "-c",
            f"import sys; sys.path.insert(0, r'{os.path.join(ROOT_DIR, 'interface')}'); from router import MoCKARouter; MoCKARouter().collaborate({repr(prompt)})"],
            cwd=ROOT_DIR)
    else:
        subprocess.Popen([sys.executable, "-c",
            f"import sys; sys.path.insert(0, r'{os.path.join(ROOT_DIR, 'interface')}'); from router import MoCKARouter; MoCKARouter().share({repr(prompt)})"],
            cwd=ROOT_DIR)
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(force=True, silent=True) or {}
    c = payload.get("c")
    o = payload.get("o")
    memo = payload.get("memo", "").strip()

    if c not in ("A", "B") or not o:
        return jsonify({"status": "error", "message": "invalid payload"}), 400

    # router.py経由で統一
    sys.path.insert(0, os.path.join(ROOT_DIR, "interface"))
    from router import MoCKARouter
    router = MoCKARouter()

    if c == "A":
        router.save(f"保存: {o}", memo if memo else "Storage mission dispatched")
    else:
        router.save(f"共有: {o}", memo if memo else "Broadcast mission dispatched")

    return jsonify({"status": "ok"})




@app.route('/collect', methods=['POST'])
def collect():
    import re as _re, csv as _csv, hashlib as _hs, json as _json
    from datetime import datetime, timezone
    from pathlib import Path as P
    d       = request.get_json()
    source  = d.get('source','unknown')
    text    = d.get('text','')
    url     = d.get('url','')
    mode    = d.get('mode','full')
    text    = _re.sub(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}','[EMAIL]',text)
    text    = _re.sub(r'sk-[A-Za-z0-9]{20,}','[APIKEY]',text)
    text    = _re.sub(r'(?i)password\s*[:=]\s*\S+','password=[MASKED]',text)
    if not text: return jsonify({'status':'empty'}),400
    INFIELD = P(r'C:/Users/sirok/MoCKA/data/storage/infield/RAW')
    EVENTS  = P(r'C:/Users/sirok/MoCKA/data/events.csv')
    INFIELD.mkdir(parents=True,exist_ok=True)
    ts      = datetime.now(timezone.utc)
    ts_str  = ts.strftime('%Y-%m-%dT%H:%M:%S')
    ts_f    = ts.strftime('%Y%m%d_%H%M%S')
    rows    = list(_csv.reader(open(EVENTS,encoding='utf-8-sig'))) if EVENTS.exists() else []
    prev    = _hs.sha256(','.join(rows[-1]).encode()).hexdigest()[:16] if rows else 'GENESIS'
    eid     = f'ECOL_{ts_f}_{source[:4].upper()}'
    h       = _hs.sha256(f'{eid}{ts_str}{text[:100]}{prev}'.encode()).hexdigest()[:16]
    rec     = {'event_id':eid,'source':source,'layer':'RAW','url':url,'mode':mode,
               'text':text,'timestamp':ts_str,'hash':h,'prev_hash':prev,'status':'RAW'}
    _json.dump(rec,open(INFIELD/f'{ts_f}_{eid}.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
    with open(EVENTS,'a',encoding='utf-8',newline='') as f:
        _csv.writer(f).writerow([eid,ts_str,source,'collect','chat_import','mocka_bridge_v2',
            url[:80],'extension','external','in_operation','normal','A','infield/RAW',
            text[:100],prev,'ingest_complete','RAW','local','chat_pipeline','N/A','N/A',
            f'hash={h}|source={source}|mode={mode}'])
    print(f'[COLLECT] {eid} from {source} ({len(text)} chars)')
    return jsonify({'status':'ok','event_id':eid,'hash':h})


@app.route('/get_intent/<ai_name>', methods=['GET'])
def get_intent(ai_name):
    return jsonify(None), 204

if __name__ == "__main__":
    print("--- MoCKA STARTING ---")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    ensure_events_csv()
    app.run(host="127.0.0.1", port=5000)
