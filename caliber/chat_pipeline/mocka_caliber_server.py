"""
mocka_caliber_server.py v4
- threaded=True（並列処理対応）
- Claude Haiku API直結（Ollamaフォールバック廃止）
- ANTHROPIC_API_KEY未設定時は即エラー返却
- 空データ自動スキップ
- PORT: 5679
"""

import csv, hashlib, json, os, re, shutil, anthropic
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ROOT       = Path("C:/Users/sirok/MoCKA")
OUTBOX     = ROOT / "data" / "storage" / "outbox" / "PILS"
PILS_DONE  = ROOT / "data" / "storage" / "outbox" / "PILS_DONE"
RE_REDUCED = ROOT / "data" / "storage" / "infield" / "RE_REDUCED"
REDUCING   = ROOT / "data" / "storage" / "infield" / "REDUCING"
EVENTS     = ROOT / "data" / "events.csv"
MODEL      = "claude-haiku-4-5-20251001"
UTC        = timezone.utc
THRESHOLD  = 0.80
CHUNK_SIZE = 3000
MAX_CHUNKS = 4

PHL_SYSTEM = """あなたはMoCKA知識蒸留エンジンです。
原則: 失敗は資産/記録が信頼の条件/AIを信じるな システムで縛れ
MoCKAの文明ループ（観測→記録→インシデント→再発→防止→決定→行動→監査）の観点から重要な洞察を抽出してください。"""

for d in [OUTBOX, PILS_DONE, RE_REDUCED, REDUCING]:
    d.mkdir(parents=True, exist_ok=True)


def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return key


def ask(prompt):
    client = anthropic.Anthropic(api_key=get_api_key())
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=PHL_SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def parse_rate(s):
    m = re.search(r"\d+", str(s))
    return int(m.group()) / 100.0 if m else 0.5


def sample_text(text):
    total = len(text)
    if total <= CHUNK_SIZE * MAX_CHUNKS:
        return [text[i:i+CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]
    step = total // MAX_CHUNKS
    return [text[step*i:step*i+CHUNK_SIZE] for i in range(MAX_CHUNKS)]


def get_prev_hash():
    if not EVENTS.exists():
        return "GENESIS"
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig")))
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"


def append_event(row):
    with open(EVENTS, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(row)


@app.route("/health", methods=["GET"])
def health():
    try:
        key = get_api_key()
        api_ok = bool(key)
    except:
        api_ok = False
    return jsonify({"status": "ok", "model": MODEL, "version": "v4", "api_key": api_ok})


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

    try:
        raw = json.load(open(fpath, encoding="utf-8-sig"))
    except Exception as e:
        done_path = PILS_DONE / (fpath.stem + "_parseerr.json")
        shutil.move(str(fpath), str(done_path))
        return jsonify({"status": "skipped", "message": "json parse error: " + str(e)})

    text = raw.get("text", raw.get("content", raw.get("summary", "")))
    if not text and "messages" in raw:
        lines = []
        for m in raw["messages"]:
            if isinstance(m, dict):
                c = m.get("content", m.get("text", ""))
                if c and len(c.strip()) > 5:
                    role = m.get("role", "")
                    lines.append(("[" + role + "] " + c) if role else c)
        text = "\n".join(lines)

    if not text or len(text.strip()) < 10:
        done_path = PILS_DONE / (fpath.stem + "_skip.json")
        shutil.move(str(fpath), str(done_path))
        return jsonify({"status": "skipped", "message": "no text"})

    source = raw.get("source", "unknown")
    event_id = raw.get("event_id", fpath.stem)
    total_chars = len(text)
    chunks = sample_text(text)

    print(f"[v4] {fpath.name} | {total_chars}chars | {len(chunks)}chunks")

    try:
        extracts = []
        for i, chunk in enumerate(chunks):
            print(f"[v4] chunk {i+1}/{len(chunks)}...")
            result = ask(
                "以下のテキストから最も重要な知的洞察を3つ、箇条書きで日本語で抽出:\n\n" + chunk
            )
            extracts.append(result)

        extract = "\n".join(extracts)

        rate_raw = ask(
            "以下の要約が元テキストの内容をどの程度保持しているか、0から100の数字のみで回答:\n\n" + extract[:1000]
        )
        rate = parse_rate(rate_raw)

    except Exception as e:
        print(f"[v4] API ERROR: {e}")
        return jsonify({"status": "error", "message": "API error: " + str(e)}), 500

    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = "EN8N_" + ts + "_" + source[:4].upper()
    h   = hashlib.sha256((eid + extract[:100]).encode()).hexdigest()[:16]
    status = "RE_REDUCED" if rate >= THRESHOLD else "REDUCING"
    dst_dir = RE_REDUCED if rate >= THRESHOLD else REDUCING

    out_data = {
        "event_id": eid, "source": source,
        "origin_file": fpath.name, "origin_event": event_id,
        "timestamp": ts, "total_chars": total_chars,
        "sampled_chunks": len(chunks), "restore_rate": rate,
        "extraction": extract, "hash": h,
        "status": status, "pipeline": "caliber_server_v04"
    }

    out = dst_dir / (ts + "_" + eid + ".json")
    json.dump(out_data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    prev = get_prev_hash()
    row = [eid, ts, "caliber_server", "process", "caliber_pipeline",
           "mocka_caliber_server.py", fpath.name, "server", "internal",
           "in_operation", "normal", "A", "infield/" + status,
           extract[:500], prev, "caliber_complete", status,
           "local", "caliber_pipeline", "N/A", "N/A",
           "hash=" + h + " rate=" + str(int(rate*100)) + "pct chars=" + str(total_chars)]
    append_event(row)

    done_name = fpath.stem + "_" + datetime.now(UTC).strftime("%H%M%S") + fpath.suffix
    done_path = PILS_DONE / done_name
    if done_path.exists():
        done_path = PILS_DONE / (fpath.stem + "_" + ts + fpath.suffix)
    fpath.rename(done_path)

    print(f"[v4] OK {status} {out.name}")
    return jsonify({
        "status": status,
        "event_id": eid,
        "restore_rate": str(int(rate*100)) + "%",
        "total_chars": total_chars,
        "extraction_preview": extract[:300]
    })


if __name__ == "__main__":
    print("[MoCKA Caliber Server v4] port 5679 threaded=True")
    try:
        get_api_key()
        print("[v4] ANTHROPIC_API_KEY: OK")
    except:
        print("[v4] WARNING: ANTHROPIC_API_KEY not set")
    app.run(host="0.0.0.0", port=5679, debug=False, threaded=True)