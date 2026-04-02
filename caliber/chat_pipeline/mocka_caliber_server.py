"""
mocka_caliber_server.py
n8nからのWebhookを受けてCaliberパイプラインを実行するFlaskサーバー
起動: python caliber/chat_pipeline/mocka_caliber_server.py
PORT: 5679
"""
import csv, hashlib, json, os, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

OLLAMA     = Path(os.environ.get("LOCALAPPDATA","")) / "Programs" / "Ollama" / "ollama.exe"
ROOT       = Path("C:/Users/sirok/MoCKA")
OUTBOX     = ROOT / "data" / "storage" / "outbox" / "PILS"
PILS_DONE  = ROOT / "data" / "storage" / "outbox" / "PILS_DONE"
RE_REDUCED = ROOT / "data" / "storage" / "infield" / "RE_REDUCED"
REDUCING   = ROOT / "data" / "storage" / "infield" / "REDUCING"
EVENTS     = ROOT / "data" / "events.csv"
MODEL      = "gemma3:4b"
UTC        = timezone.utc
THRESHOLD  = 0.80

for d in [OUTBOX, PILS_DONE, RE_REDUCED, REDUCING]:
    d.mkdir(parents=True, exist_ok=True)

def ask(prompt):
    r = subprocess.run([str(OLLAMA),"run",MODEL,prompt],
        capture_output=True,text=True,encoding="utf-8",timeout=120)
    return r.stdout.strip()

def get_prev():
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig"))) if EVENTS.exists() else []
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"

def parse_rate(s):
    m = re.search(r"\d+", s)
    return int(m.group()) / 100.0 if m else 0.0

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL})

@app.route("/scan", methods=["GET"])
def scan():
    files = list(OUTBOX.glob("*.json"))
    return jsonify({"count": len(files), "files": [f.name for f in files[:10]]})

@app.route("/process", methods=["POST"])
def process():
    data = request.json or {}
    fname = data.get("file")
    if fname:
        fpath = OUTBOX / fname
    else:
        files = sorted(OUTBOX.glob("*.json"), key=lambda x: x.stat().st_mtime)
        if not files:
            return jsonify({"status": "empty", "message": "no files in outbox/PILS"})
        fpath = files[0]

    if not fpath.exists():
        return jsonify({"status": "error", "message": str(fpath) + " not found"}), 404

    raw = json.load(open(fpath, encoding="utf-8"))
    text = raw.get("text", raw.get("content", raw.get("summary", "")))
    source = raw.get("source", "unknown")
    event_id = raw.get("event_id", fpath.stem)

    if not text:
        return jsonify({"status": "error", "message": "no text field"}), 400

    print("[CALIBER] extract:", fpath.name)
    extract = ask("Extract the 3 most important structural insights as bullet points:\n\n" + text[:3000])

    print("[CALIBER] shadow eval...")
    rate_raw = ask("Estimate what percentage (0-100) of the original meaning is preserved in this summary. Reply ONLY with a number.\n\nSummary: " + extract[:2000])
    rate = parse_rate(rate_raw)

    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = "EN8N_" + ts + "_" + source[:4].upper()
    h   = hashlib.sha256((eid + ts + extract[:100]).encode()).hexdigest()[:16]
    status = "RE_REDUCED" if rate >= THRESHOLD else "REDUCING"

    result = {
        "event_id": eid, "source": source,
        "origin_file": fpath.name, "origin_event": event_id,
        "timestamp": ts, "restore_rate": rate,
        "threshold": THRESHOLD, "extraction": extract,
        "hash": h, "status": status, "pipeline": "caliber_server_v01"
    }

    dst_dir = RE_REDUCED if rate >= THRESHOLD else REDUCING
    out = dst_dir / (ts + "_" + eid + ".json")
    json.dump(result, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

    prev = get_prev()
    with open(EVENTS,"a",encoding="utf-8",newline="") as f:
        csv.writer(f).writerow([eid,ts,"caliber_server","process","caliber_pipeline",
            "mocka_caliber_server.py",fpath.name,"server","internal",
            "in_operation","normal","A","infield/"+status,
            extract[:100],prev,"caliber_complete",status,
            "local","caliber_pipeline","N/A","N/A",
            "hash="+h+" rate="+str(int(rate*100))+"pct source="+source])

    fpath.rename(PILS_DONE / fpath.name)
    print("[OK]", status, out.name)

    return jsonify({
        "status": status,
        "event_id": eid,
        "restore_rate": str(int(rate*100)) + "%",
        "saved": str(out),
        "extraction_preview": extract[:200]
    })

@app.route("/process_all", methods=["POST"])
def process_all():
    files = sorted(OUTBOX.glob("*.json"), key=lambda x: x.stat().st_mtime)
    if not files:
        return jsonify({"status": "empty", "processed": 0})
    results = []
    for f in files:
        r = process.__wrapped__({"file": f.name}) if hasattr(process, "__wrapped__") else None
        results.append(f.name)
    return jsonify({"status": "ok", "queued": len(results), "files": results})

if __name__ == "__main__":
    print("[MoCKA Caliber Server] starting on port 5679...")
    print("[INFO] Ollama:", OLLAMA)
    print("[INFO] Outbox:", OUTBOX)
    app.run(host="0.0.0.0", port=5679, debug=False)