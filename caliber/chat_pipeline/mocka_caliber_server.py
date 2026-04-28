"""
mocka_caliber_server.py v5
APIゼロ化版 - Claude Haiku API呼び出しをローカル処理に完全置き換え

変更点:
  - ask() → extract_local() / calc_rate_local() に置き換え
  - anthropic import 削除
  - 重要文抽出: キーワードスコアリング + TF-IDF風スコア
  - restore_rate: キーワード密度 + 文章密度から算出
  - pattern_engine_v2 のキーワードリストを活用
  - PORT: 5679 (変更なし)

Author: Claude (執行官)  Date: 2026-04-27
"""

import csv, hashlib, json, os, re, shutil
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

UTC        = timezone.utc
THRESHOLD  = 0.60   # v5: APIなしなので閾値を下げる（v4は0.80）
CHUNK_SIZE = 3000
MAX_CHUNKS = 4

for d in [OUTBOX, PILS_DONE, RE_REDUCED, REDUCING]:
    d.mkdir(parents=True, exist_ok=True)

# ─── パターンエンジン読み込み（キーワードリスト活用） ────────────────────────
try:
    import sys
    sys.path.insert(0, str(ROOT / "interface"))
    from pattern_engine_v2 import PatternEngine as _PE
    _engine = _PE()
    IMPORTANT_KEYWORDS = (
        [r["pattern"] for r in _engine.registry.danger_keywords()] +
        [r["pattern"] for r in _engine.registry.success_keywords()]
    )
    print(f"[v5] pattern_engine: {len(IMPORTANT_KEYWORDS)} keywords loaded")
except Exception as e:
    IMPORTANT_KEYWORDS = []
    print(f"[v5] pattern_engine unavailable: {e}")

# 汎用重要語リスト（パターンエンジンが使えない場合のフォールバック）
FALLBACK_KEYWORDS = [
    "完了", "エラー", "修正", "実装", "確認", "問題", "解決", "インシデント",
    "記録", "更新", "追加", "削除", "変更", "設計", "実行", "検証",
    "失敗", "成功", "警告", "注意", "重要", "TODO", "DONE", "CRITICAL",
    "MoCKA", "pattern", "engine", "caliber", "essence",
]


def get_keywords():
    return IMPORTANT_KEYWORDS if IMPORTANT_KEYWORDS else FALLBACK_KEYWORDS


# ─── ローカル抽出エンジン ─────────────────────────────────────────────────────

def score_sentence(sentence: str, keywords: list[str]) -> float:
    """文にスコアを付ける。キーワード含有数・文の長さ・記号の存在で評価。"""
    s = sentence.strip()
    if not s or len(s) < 8:
        return 0.0

    score = 0.0

    # キーワードヒット（最大5点）
    kw_hits = sum(1 for kw in keywords if kw in s)
    score += min(kw_hits * 1.5, 5.0)

    # 適切な文長（20〜200文字が理想）
    l = len(s)
    if 20 <= l <= 200:
        score += 1.5
    elif l > 200:
        score += 0.5

    # 数字・記号を含む（具体的な情報）
    if re.search(r'\d', s):
        score += 0.5
    if re.search(r'[：:→=]', s):
        score += 0.3

    # 否定・問題系ワードを含む
    if re.search(r'(エラー|失敗|問題|できない|動かない|なぜ)', s):
        score += 1.0

    # 完了・成果系ワードを含む
    if re.search(r'(完了|成功|確認|修正済|OK|PASS)', s):
        score += 1.0

    return score


def extract_local(text: str, max_sentences: int = 15) -> str:
    """テキストから重要文を抽出してローカルで要約を生成する。"""
    keywords = get_keywords()

    # 文分割（。！？\n で分割）
    raw_sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) >= 8]

    if not sentences:
        return text[:500]

    # スコアリング
    scored = [(score_sentence(s, keywords), s) for s in sentences]
    scored.sort(key=lambda x: -x[0])

    # 上位N文を元の順序で返す
    top_set = set(s for _, s in scored[:max_sentences] if _ > 0)
    ordered = [s for s in sentences if s in top_set]

    if not ordered:
        ordered = [s for _, s in scored[:5]]

    return "。\n".join(ordered)


def calc_rate_local(text: str, extraction: str) -> float:
    """
    APIなしでrestore_rateを推定する。
    キーワード密度・抽出率・文数から算出。
    """
    if not text or not extraction:
        return 0.3

    keywords = get_keywords()

    # 抽出率（文字数比）
    char_ratio = min(len(extraction) / max(len(text), 1), 1.0)

    # キーワード密度（抽出文中にキーワードがどれだけあるか）
    kw_hits = sum(1 for kw in keywords if kw in extraction)
    kw_density = min(kw_hits / max(len(keywords) * 0.1, 1), 1.0)

    # 文数（多いほど情報量あり）
    sentence_count = len([s for s in re.split(r'[。\n]', extraction) if len(s.strip()) > 5])
    sentence_score = min(sentence_count / 10.0, 1.0)

    # 重み付き合計
    rate = (char_ratio * 0.3) + (kw_density * 0.5) + (sentence_score * 0.2)
    return round(min(max(rate, 0.1), 1.0), 3)


# ─── ユーティリティ ──────────────────────────────────────────────────────────

def sample_text(text: str) -> list[str]:
    total = len(text)
    if total <= CHUNK_SIZE * MAX_CHUNKS:
        return [text[i:i+CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]
    step = total // MAX_CHUNKS
    return [text[step*i:step*i+CHUNK_SIZE] for i in range(MAX_CHUNKS)]


def get_prev_hash() -> str:
    if not EVENTS.exists():
        return "GENESIS"
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig")))
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"


def append_event(row):
    try:
        with open(EVENTS, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception as e:
        print(f"[caliber] CSV error: {e}")
    try:
        db = Path("C:/Users/sirok/MoCKA/data/mocka_events.db")
        cols = ["event_id","when_ts","who_actor","what_type","where_component","where_path","why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level","category_ab","target_class","title","short_summary","before_state","after_state","change_type","impact_scope","impact_result","related_event_id","trace_id","free_note"]
        padded = (list(row) + [""]*23)[:23]
        padded += [datetime.now(timezone.utc).isoformat(),"caliber_server","caliber","","normal",0.0,0,"caliber_v5"]
        all_cols = cols + ["_imported_at","_source","ai_actor","session_id","severity","pattern_score","recurrence_flag","verified_by"]
        ph = ",".join(["?"]*len(all_cols))
        sql = f"INSERT OR IGNORE INTO events ({','.join(all_cols)}) VALUES ({ph})"
        conn = sqlite3.connect(str(db), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(sql, padded)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[caliber] SQLite error: {e}")


# ─── エンドポイント ───────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":   "ok",
        "version":  "v5",
        "mode":     "api_zero",
        "keywords": len(get_keywords()),
        "threshold": THRESHOLD,
    })


@app.route("/scan", methods=["GET"])
def scan():
    files = list(OUTBOX.glob("*.json"))
    return jsonify({"count": len(files), "files": [f.name for f in files[:10]]})


@app.route("/process", methods=["POST"])
def process():
    data  = request.json or {}
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

    # テキスト抽出
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

    source    = raw.get("source", "unknown")
    event_id  = raw.get("event_id", fpath.stem)
    total_chars = len(text)
    chunks    = sample_text(text)

    print(f"[v5] {fpath.name} | {total_chars}chars | {len(chunks)}chunks")

    # ─── ローカル処理（APIゼロ） ───────────────────────────────────────────
    extracts = []
    for i, chunk in enumerate(chunks):
        print(f"[v5] chunk {i+1}/{len(chunks)} local extract...")
        extracts.append(extract_local(chunk))

    extraction = "\n---\n".join(extracts)
    rate       = calc_rate_local(text, extraction)
    # ─────────────────────────────────────────────────────────────────────

    ts     = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid    = "EN8N_" + ts + "_" + source[:4].upper()
    h      = hashlib.sha256((eid + extraction[:100]).encode()).hexdigest()[:16]
    status  = "RE_REDUCED" if rate >= THRESHOLD else "REDUCING"
    dst_dir = RE_REDUCED  if rate >= THRESHOLD else REDUCING

    out_data = {
        "event_id": eid, "source": source,
        "origin_file": fpath.name, "origin_event": event_id,
        "timestamp": ts, "total_chars": total_chars,
        "sampled_chunks": len(chunks), "restore_rate": rate,
        "extraction": extraction, "hash": h,
        "status": status, "pipeline": "caliber_server_v05_api_zero"
    }

    out = dst_dir / (ts + "_" + eid + ".json")
    json.dump(out_data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    prev = get_prev_hash()
    row  = [eid, ts, "caliber_server", "process", "caliber_pipeline",
            "mocka_caliber_server.py", fpath.name, "server", "internal",
            "in_operation", "normal", "A", "infield/" + status,
            extraction[:500], prev, "caliber_complete", status,
            "local", "caliber_pipeline", "N/A", "N/A",
            "hash=" + h + " rate=" + str(int(rate*100)) + "pct chars=" + str(total_chars)]
    append_event(row)

    done_name = fpath.stem + "_" + datetime.now(UTC).strftime("%H%M%S") + fpath.suffix
    done_path = PILS_DONE / done_name
    if done_path.exists():
        done_path = PILS_DONE / (fpath.stem + "_" + ts + fpath.suffix)
    fpath.rename(done_path)

    print(f"[v5] OK {status} rate={int(rate*100)}% {out.name}")
    return jsonify({
        "status":            status,
        "event_id":          eid,
        "restore_rate":      str(int(rate*100)) + "%",
        "total_chars":       total_chars,
        "mode":              "api_zero",
        "extraction_preview": extraction[:300],
    })



# ============================================================
# 自動RAW処理ループ（15秒間隔でRAWフォルダを監視）
# ============================================================
import threading as _threading
import time as _time

RAW_INFIELD = ROOT / "data" / "storage" / "infield" / "RAW"

def auto_raw_loop():
    print("[AUTO-RAW] 自動RAW処理ループ開始")
    RAW_INFIELD.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            files = list(RAW_INFIELD.glob("*.json"))
            if files:
                print(f"[AUTO-RAW] {len(files)}件検出 -> 自動処理開始")
                for fpath in files:
                    try:
                        _process_raw_file(fpath)
                    except Exception as e:
                        print(f"[AUTO-RAW] エラー({fpath.name}): {str(e)[:80]}")
        except Exception as e:
            print(f"[AUTO-RAW] ループ例外: {str(e)[:80]}")
        _time.sleep(15)

def _process_raw_file(fpath):
    try:
        raw = json.load(open(fpath, encoding="utf-8-sig"))
    except Exception:
        raw = json.loads(fpath.read_bytes().decode("utf-8", errors="replace"))
    text = raw.get("text", raw.get("content", raw.get("summary", "")))
    if not text and "messages" in raw:
        for m in raw["messages"]:
            if isinstance(m, dict):
                text += m.get("content", "") + "\n"
    if not text:
        text = str(raw)
    source    = raw.get("source", "unknown")
    event_id  = raw.get("event_id", fpath.stem)
    total_chars = len(text)
    chunks    = sample_text(text)
    keywords  = get_keywords()
    sentences = []
    for chunk in chunks:
        for s in re.split(r'[。！？\n]', chunk):
            s = s.strip()
            if len(s) >= 8:
                sentences.append(s)
    scored = sorted(
        [(s, score_sentence(s, keywords)) for s in sentences],
        key=lambda x: x[1], reverse=True
    )
    extraction = "。".join([s for s, _ in scored[:15]])
    rate       = calc_rate_local(text, extraction)
    ts      = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid     = "ENRAW_" + ts + "_" + source[:4].upper()
    h       = hashlib.sha256((eid + extraction[:100]).encode()).hexdigest()[:16]
    status  = "RE_REDUCED" if rate >= THRESHOLD else "REDUCING"
    dst_dir = RE_REDUCED  if rate >= THRESHOLD else REDUCING
    out_data = {
        "event_id": eid, "source": source,
        "origin_file": fpath.name, "origin_event": event_id,
        "timestamp": ts, "total_chars": total_chars,
        "sampled_chunks": len(chunks), "restore_rate": rate,
        "extraction": extraction, "hash": h,
        "status": status, "pipeline": "auto_raw_loop_v1"
    }
    out = dst_dir / (ts + "_" + eid + ".json")
    json.dump(out_data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    prev = get_prev_hash()
    row  = [eid, ts, "auto_raw_loop", "process", "caliber_pipeline",
            "mocka_caliber_server.py", fpath.name, "server", "internal",
            "in_operation", "normal", "A", "infield/" + status,
            extraction[:500], prev, "auto_raw_complete", status,
            "local", "caliber_pipeline", "N/A", "N/A",
            "hash=" + h + " rate=" + str(int(rate*100)) + "pct chars=" + str(total_chars)]
    append_event(row)
    archive = ROOT / "data" / "storage" / "infield" / "ARCHIVED"
    archive.mkdir(parents=True, exist_ok=True)
    done_name = fpath.stem + "_" + datetime.now(UTC).strftime("%H%M%S") + fpath.suffix
    done_path = archive / done_name
    if done_path.exists():
        done_path = archive / (fpath.stem + "_" + ts + fpath.suffix)
    fpath.rename(done_path)
    print(f"[AUTO-RAW] OK {status} rate={int(rate*100)}% {out.name}")

_auto_raw_thread = _threading.Thread(target=auto_raw_loop, daemon=True)
_auto_raw_thread.start()
if __name__ == "__main__":
    print("[MoCKA Caliber Server v5 - API ZERO] port 5679")
    print(f"[v5] keywords: {len(get_keywords())}")
    print(f"[v5] threshold: {THRESHOLD}")
    app.run(host="0.0.0.0", port=5679, debug=False, threaded=True)

