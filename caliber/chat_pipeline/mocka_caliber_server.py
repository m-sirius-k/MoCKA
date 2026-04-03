"""
mocka_caliber_server.py v2
バッチ処理対応: 大容量ファイルをサンプリング処理
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
CHUNK_SIZE = 2000
MAX_CHUNKS = 5
TIMEOUT    = 300

for d in [OUTBOX, PILS_DONE, RE_REDUCED, REDUCING]:
    d.mkdir(parents=True, exist_ok=True)

def ask(prompt):
    r = subprocess.run([str(OLLAMA),"run",MODEL,prompt],
        capture_output=True,text=True,encoding="utf-8",timeout=TIMEOUT)
    return r.stdout.strip()

def get_prev():
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig"))) if EVENTS.exists() else []
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"

def parse_rate(s):
    m = re.search(r"\d+", s)
    return int(m.group()) / 100.0 if m else 0.5

def sample_text(text, chunk_size=CHUNK_SIZE, max_chunks=MAX_CHUNKS):
    total = len(text)
    if total <= chunk_size * max_chunks:
        return [text[i:i+chunk_size] for i in range(0, total, chunk_size)]
    chunks = []
    step = total // max_chunks
    for i in range(max_chunks):
        start = step * i
        chunks.append(text[start:start+chunk_size])
    return chunks

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL, "version": "v2"})

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
    total_chars = len(text)
    chunks = sample_text(text)
    print(f"[CALIBER] {fpath.name} | {total_chars} chars | {len(chunks)} chunks (sampled)")
    all_extracts = []
    for i, chunk in enumerate(chunks):
        print(f"[CALIBER] extract chunk {i+1}/{len(chunks)}...")
        result = ask("以下のテキストから最も重要な構造的洞察を3つ、箇条書きで日本語で抽出してください:\n\n" + chunk)
        all_extracts.append(result)
    extract = chr(10).join(all_extracts)
    print("[CALIBER] shadow eval...")
    rate_raw = ask("以下の要約が元の文章の意味をどの程度保持しているか、0から100の数字のみで回答してください。\n\n要約: " + extract[:2000])
    rate = parse_rate(rate_raw)
    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = "EN8N_" + ts + "_" + source[:4].upper()
    h   = hashlib.sha256((eid + ts + extract[:100]).encode()).hexdigest()[:16]
    status = "RE_REDUCED" if rate >= THRESHOLD else "REDUCING"
    result = {
        "event_id": eid, "source": source,
        "origin_file": fpath.name, "origin_event": event_id,
        "timestamp": ts, "total_chars": total_chars,
        "sampled_chunks": len(chunks), "restore_rate": rate,
        "threshold": THRESHOLD, "extraction": extract,
        "hash": h, "status": status, "pipeline": "caliber_server_v02"
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
            "hash="+h+" rate="+str(int(rate*100))+"pct chars="+str(total_chars)+" chunks="+str(len(chunks))])
    done_name = fpath.stem + "_" + datetime.now(UTC).strftime("%H%M%S") + fpath.suffix
    done_path = PILS_DONE / done_name
    if done_path.exists(): done_path = PILS_DONE / (fpath.stem + "_" + str(int(datetime.now(UTC).timestamp())) + fpath.suffix)
    fpath.rename(done_path)
    print("[OK]", status, out.name)
    return jsonify({
        "status": status, "event_id": eid,
        "restore_rate": str(int(rate*100)) + "%",
        "total_chars": total_chars, "sampled_chunks": len(chunks),
        "saved": str(out), "extraction_preview": extract[:200]
    })

if __name__ == "__main__":
    print("[MoCKA Caliber Server v2] starting on port 5679...")
    print(f"[INFO] Ollama: {OLLAMA}")
    print(f"[INFO] Outbox: {OUTBOX}")
    print(f"[INFO] Chunk: {CHUNK_SIZE} chars x max {MAX_CHUNKS} (sampling)")
    app.run(host="0.0.0.0", port=5679, debug=False)