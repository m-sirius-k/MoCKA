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


"""
mocka_caliber_server_phl_patch.py
======================================
mocka_caliber_server.py v5 縺ｸ縺ｮ PHL-OS 霑ｽ蜉繝代ャ繝・
縲宣←逕ｨ譁ｹ豕輔・mocka_caliber_server.py 縺ｮ譛ｫ蟆ｾ・・f __name__ == "__main__": 縺ｮ逶ｴ蜑搾ｼ峨↓
縺薙・繝輔ぃ繧､繝ｫ縺ｮ蜀・ｮｹ繧偵◎縺ｮ縺ｾ縺ｾ繧ｳ繝斐・&繝壹・繧ｹ繝医☆繧九・
霑ｽ蜉繧ｨ繝ｳ繝峨・繧､繝ｳ繝・
  POST /phl/analyze       竊・PHL-OS 繝｡繧､繝ｳ螳溯｡・  GET  /phl/history       竊・逶ｴ霑・decision_trace 荳隕ｧ
  GET  /phl/modules       竊・繝｢繧ｸ繝･繝ｼ繝ｫ螳夂ｾｩ遒ｺ隱・
譌｢蟄倥さ繝ｼ繝峨・荳蛻・､画峩縺励↑縺・・======================================
Author: Claude (蝓ｷ陦悟ｮ・  Date: 2026-04-29
"""

import sqlite3  # append_event 縺ｧ譌｢縺ｫ菴ｿ逕ｨ荳ｭ縺縺悟ｿｵ縺ｮ縺溘ａ

# 笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊・# PHL-OS 窶・繧､繝ｳ繝ｩ繧､繝ｳ螳溯｣・ｼ亥､夜Κ萓晏ｭ倥ぞ繝ｭ・・# 笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊・
# 笏笏 繝｢繧ｸ繝･繝ｼ繝ｫ迚ｹ諤ｧ繝・・繝悶Ν 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
PHL_MODULE_SPECS = {
    "ghost":      {"precision":0.95,"structure":0.55,"speed":0.70,"stability":0.95,"risk":0.15,
                   "desc":"邊ｾ蠎ｦ繝ｻ蜀ｷ蜊ｴ繝｢繝ｼ繝・},
    "L99":        {"precision":0.80,"structure":0.95,"speed":0.55,"stability":0.80,"risk":0.25,
                   "desc":"讒矩蛹悶・險育判繝｢繝ｼ繝・},
    "OODA":       {"precision":0.70,"structure":0.70,"speed":0.90,"stability":0.60,"risk":0.45,
                   "desc":"諢乗晄ｱｺ螳壹Ν繝ｼ繝励・騾溷ｺｦ蜆ｪ蜈・},
    "SAGE":       {"precision":0.75,"structure":0.65,"speed":0.40,"stability":0.70,"risk":0.35,
                   "desc":"謚ｽ雎｡蛹悶・諤晄Φ謚ｽ蜃ｺ"},
    "STRATEGIST": {"precision":0.82,"structure":0.88,"speed":0.50,"stability":0.82,"risk":0.28,
                   "desc":"髟ｷ譛溯ｨｭ險医・繝ｭ繝ｼ繝峨・繝・・"},
    "artifact":   {"precision":0.72,"structure":0.92,"speed":0.72,"stability":0.78,"risk":0.20,
                   "desc":"謌先棡迚ｩ逕滓・繝ｻ蜃ｺ蜉帛崋螳壼喧"},
    "code":       {"precision":0.85,"structure":0.78,"speed":0.68,"stability":0.74,"risk":0.40,
                   "desc":"螳溯｣・喧繝ｻ繧ｳ繝ｼ繝臥函謌・},
}

# 笏笏 state_vector 繝薙Ν繝繝ｼ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_build_state(payload: dict) -> dict:
    return {
        "goal_type":              payload.get("goal_type", "analysis"),
        "uncertainty":            float(payload.get("uncertainty", 0.5)),
        "risk_level":             float(payload.get("risk_level", 0.3)),
        "time_pressure":          float(payload.get("time_pressure", 0.3)),
        "abstraction_level":      float(payload.get("abstraction_level", 0.5)),
        "novelty":                float(payload.get("novelty", 0.4)),
        "output_format":          payload.get("output_format", ["text"]),
        "evidence_required":      float(payload.get("evidence_required", 0.5)),
        "reversibility_required": float(payload.get("reversibility_required", 0.5)),
        "stakes":                 payload.get("stakes", "medium"),
    }

# 笏笏 繝｢繧ｸ繝･繝ｼ繝ｫ驕ｸ謚・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_select_modules(state: dict):
    candidates = []

    if state["uncertainty"] >= 0.6 or state["evidence_required"] >= 0.7:
        candidates.append({"module":"ghost",      "trigger":"uncertainty>=0.6 or evidence_required>=0.7"})
    if "plan" in state["output_format"] or state["abstraction_level"] >= 0.6:
        candidates.append({"module":"L99",        "trigger":"plan in output_format or abstraction_level>=0.6"})
    if state["goal_type"] == "decision" or state["time_pressure"] >= 0.7:
        candidates.append({"module":"OODA",       "trigger":"goal_type==decision or time_pressure>=0.7"})
    if state["goal_type"] in ["design","review"] and state["abstraction_level"] >= 0.7:
        candidates.append({"module":"SAGE",       "trigger":"goal_type in [design,review] and abstraction_level>=0.7"})
        candidates.append({"module":"STRATEGIST", "trigger":"goal_type in [design,review] and abstraction_level>=0.7"})
    if "code" in state["output_format"] or state["goal_type"] == "implementation":
        candidates.append({"module":"code",       "trigger":"code in output_format or goal_type==implementation"})
    if "table" in state["output_format"]:
        candidates.append({"module":"artifact",   "trigger":"table in output_format"})
    if not candidates:
        candidates.append({"module":"ghost",      "trigger":"fallback:no_match"})

    # 遶ｶ蜷郁ｧ｣豸・    selected = list(dict.fromkeys(c["module"] for c in candidates))
    excluded = []
    if "ghost" in selected and "high_creative" in selected and state["risk_level"] > 0.4:
        selected.remove("high_creative")
        excluded.append({"module":"high_creative","reason":"conflict:ghost:risk>0.4"})
    if "OODA" in selected and "SAGE" in selected and state["time_pressure"] > 0.7:
        selected.remove("SAGE")
        excluded.append({"module":"SAGE","reason":"conflict:OODA:time_pressure>0.7"})

    return selected, candidates, excluded

# 笏笏 繧ｬ繝ｼ繝牙愛螳・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_run_guard(state: dict, modules: list, draft: dict) -> dict:
    risk = state.get("risk_level", 0.0)
    rev  = state.get("reversibility_required", 0.0)
    ev_r = state.get("evidence_required", 0.0)
    ev_c = draft.get("evidence_count", 1)
    contradiction = draft.get("contradiction", False)

    if contradiction:
        return {"status":"HALT",      "level":4, "reason":"logical_contradiction"}
    if risk > 0.75 and rev > 0.7:
        return {"status":"HALT",      "level":4, "reason":"high_risk_irreversible"}
    if risk > 0.9:
        return {"status":"HALT",      "level":4, "reason":"extreme_risk"}
    if ev_r > 0.8 and ev_c == 0:
        return {"status":"REANALYZE", "level":3, "reason":"insufficient_evidence"}
    if risk > 0.75:
        return {"status":"RESTRICT",  "level":2, "reason":f"risk={risk:.2f}:modules_limited"}
    if risk > 0.6:
        return {"status":"WARN",      "level":1, "reason":f"risk={risk:.2f}:elevated"}
    return {"status":"SAFE",          "level":0, "reason":None}

# 笏笏 繧ｹ繧ｳ繧｢險育ｮ・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_score(module: str, state: dict) -> float:
    spec = PHL_MODULE_SPECS.get(module, {})
    if not spec:
        return 0.5
    score  = spec.get("precision", 0.5) * (0.3 + state.get("uncertainty", 0.5) * 0.2)
    score += spec.get("structure", 0.5) * (0.2 + state.get("abstraction_level", 0.5) * 0.2)
    score += spec.get("speed",     0.5) * state.get("time_pressure", 0.3) * 0.2
    score -= spec.get("risk",      0.3) * state.get("risk_level", 0.3) * 0.3
    return round(score, 4)

# 笏笏 decision_trace 逕滓・ 笘・ｸ蠢・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_build_trace(state, candidates, selected, excluded, guard) -> dict:
    all_mods = [c["module"] for c in candidates]
    not_selected = [m for m in all_mods if m not in selected]

    scores = {m: phl_score(m, state) for m in all_mods}
    selected_reasons = {c["module"]: c["trigger"]
                        for c in candidates if c["module"] in selected}
    weights = {
        "precision_weight": round(0.3 + state.get("uncertainty", 0.5) * 0.2, 3),
        "structure_weight": round(0.2 + state.get("abstraction_level", 0.5) * 0.2, 3),
        "speed_weight":     round(state.get("time_pressure", 0.3) * 0.2, 3),
        "risk_penalty":     round(state.get("risk_level", 0.3) * 0.3, 3),
    }
    counterfactuals = []
    for m in not_selected:
        spec = PHL_MODULE_SPECS.get(m, {})
        reason = "not triggered by state_vector"
        if m == "SAGE" and state.get("time_pressure", 0) > 0.7:
            reason = "time_pressure>0.7: OODA priority"
        elif spec.get("risk", 0) > 0.7:
            reason = f"module_risk={spec.get('risk')}: too high"
        counterfactuals.append({
            "module":              m,
            "score":               phl_score(m, state),
            "expected_effect":     spec.get("desc", "窶・),
            "reason_not_selected": reason,
        })

    return {
        "version": "v1",
        "state_summary": {
            "goal_type":  state.get("goal_type"),
            "uncertainty": state.get("uncertainty"),
            "risk_level": state.get("risk_level"),
            "stakes":     state.get("stakes"),
        },
        "candidate_modules":  all_mods,
        "scores":             scores,
        "weights":            weights,
        "selected":           selected,
        "selected_reasons":   selected_reasons,
        "excluded":           excluded,
        "guard_status":       guard.get("status"),
        "guard_reason":       guard.get("reason"),
        "counterfactuals":    counterfactuals,
    }

# 笏笏 events.csv 縺ｸ險倬鹸 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def phl_record_event(state: dict, selected: list, guard: dict, trace: dict):
    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = f"EPHL_{ts}_{state.get('goal_type','?')[:4].upper()}"
    prev = get_prev_hash()  # 譌｢蟄倬未謨ｰ繧呈ｵ∫畑

    reasons_str = json.dumps(trace.get("selected_reasons", {}), ensure_ascii=False)
    trace_str   = json.dumps(trace, ensure_ascii=False)

    row = [
        eid, ts, "PHL-OS", "phl_decision", "caliber/phl_os",
        "mocka_caliber_server.py", reasons_str, "phl_analyze",
        "internal", "in_operation", "normal", "A",
        f"selected:{','.join(selected)}",
        f"PHL-OS: {state.get('goal_type')} 竊・{','.join(selected)}",
        prev, f"guard:{guard.get('status')} stakes:{state.get('stakes')}",
        "phl_decision", "caliber", "decision_trace",
        "N/A", "N/A",
        f"guard={guard.get('status')} trace={trace_str[:200]}",
    ]
    append_event(row)  # 譌｢蟄倬未謨ｰ繧呈ｵ∫畑
    return eid

# 笏笏 逶ｴ霑代ヨ繝ｬ繝ｼ繧ｹ菫晏ｭ假ｼ医Γ繝｢繝ｪ蜀・∵怙螟ｧ50莉ｶ・・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
_phl_history = []

def _phl_push_history(entry: dict):
    _phl_history.append(entry)
    if len(_phl_history) > 50:
        _phl_history.pop(0)


# 笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊・# Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝・# 笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊絶武笊・
@app.route("/phl/analyze", methods=["POST"])
def phl_analyze():
    """
    PHL-OS 繝｡繧､繝ｳ螳溯｡後お繝ｳ繝峨・繧､繝ｳ繝医・
    Request body (JSON):
    {
      "state": {
        "goal_type": "design",          // analysis/design/decision/implementation/review
        "uncertainty": 0.7,             // 0.0縲・.0
        "risk_level": 0.4,
        "time_pressure": 0.3,
        "abstraction_level": 0.8,
        "novelty": 0.6,
        "output_format": ["plan","code"],
        "evidence_required": 0.7,
        "reversibility_required": 0.8,
        "stakes": "high"               // low/medium/high
      },
      "draft": {                        // 繧ｪ繝励す繝ｧ繝ｳ
        "evidence_count": 2,
        "contradiction": false
      }
    }

    Response:
    {
      "event_id": "EPHL_...",
      "selected_modules": [...],
      "guard": { "status": "SAFE", ... },
      "decision_trace": { ... },        // 笘・縺ｪ縺懊◎縺ｮ蛻､譁ｭ縺・      "recorded": true
    }
    """
    body  = request.json or {}
    payload = body.get("state", body)   # state 繧ｭ繝ｼ縺後↑縺代ｌ縺ｰ body 蜈ｨ菴薙ｒ state 縺ｨ縺励※謇ｱ縺・    draft   = body.get("draft", {"evidence_count": 1, "contradiction": False})

    # 繝代う繝励Λ繧､繝ｳ螳溯｡・    state             = phl_build_state(payload)
    selected, candidates, excluded = phl_select_modules(state)
    guard             = phl_run_guard(state, selected, draft)
    trace             = phl_build_trace(state, candidates, selected, excluded, guard)
    eid               = phl_record_event(state, selected, guard, trace)

    result = {
        "event_id":        eid,
        "selected_modules": selected,
        "guard":           guard,
        "decision_trace":  trace,
        "recorded":        True,
    }
    _phl_push_history(result)

    print(f"[PHL-OS] {eid} | modules={selected} | guard={guard['status']}")
    return jsonify(result)


@app.route("/phl/history", methods=["GET"])
def phl_history():
    """逶ｴ霑・decision_trace 荳隕ｧ・域怙螟ｧ50莉ｶ縲√Γ繝｢繝ｪ蜀・ｼ・""
    n = int(request.args.get("n", 10))
    return jsonify({
        "count":   len(_phl_history),
        "history": _phl_history[-n:],
    })


@app.route("/phl/modules", methods=["GET"])
def phl_modules():
    """繝｢繧ｸ繝･繝ｼ繝ｫ螳夂ｾｩ荳隕ｧ"""
    return jsonify({
        "modules": PHL_MODULE_SPECS,
        "count":   len(PHL_MODULE_SPECS),
        "version": "v1",
    })

if __name__ == "__main__":
    print("[MoCKA Caliber Server v5 - API ZERO] port 5679")
    print(f"[v5] keywords: {len(get_keywords())}")
    print(f"[v5] threshold: {THRESHOLD}")
    app.run(host="0.0.0.0", port=5679, debug=False, threaded=True)




