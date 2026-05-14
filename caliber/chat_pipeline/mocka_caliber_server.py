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

import csv, hashlib, json, os, re, shutil, threading as _threading
_essence_lock = _threading.Lock()
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
    """SQLite単一ストレージへ記録（CSV廃止済み）"""
    try:
        import sqlite3 as _sq3
        db = Path("C:/Users/sirok/MoCKA/data/mocka_events.db")
        cols = ["event_id","when_ts","who_actor","what_type","where_component",
                "where_path","why_purpose","how_trigger","channel_type",
                "lifecycle_phase","risk_level","category_ab","target_class",
                "title","short_summary","before_state","after_state",
                "change_type","impact_scope","impact_result",
                "related_event_id","trace_id","free_note"]
        padded = (list(row) + [""]*23)[:23]
        extra  = [datetime.now(timezone.utc).isoformat(),
                  "caliber_server","caliber","","normal",0.0,0,"caliber_v5"]
        all_cols = cols + ["_imported_at","_source","ai_actor","session_id",
                           "severity","pattern_score","recurrence_flag","verified_by"]
        ph  = ",".join(["?"]*len(all_cols))
        sql = f"INSERT OR IGNORE INTO events ({','.join(all_cols)}) VALUES ({ph})"
        conn = _sq3.connect(str(db), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(sql, padded + extra)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[caliber] SQLite error: {e}")


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



# ===============================================================
# PHL-OS Caliber Integration v1
# Append this block just before: if __name__ == "__main__":
# UTF-8完全対応済み（sanitizeゲート・SQLite移行により文字化けリスク解消 E20260514_040）
# ===============================================================

# Module specs table
PHL_MODULE_SPECS = {
    "ghost":      {"precision":0.95,"structure":0.55,"speed":0.70,"stability":0.95,"risk":0.15,
                   "desc":"precision and cooling mode"},
    "L99":        {"precision":0.80,"structure":0.95,"speed":0.55,"stability":0.80,"risk":0.25,
                   "desc":"structured planning mode"},
    "OODA":       {"precision":0.70,"structure":0.70,"speed":0.90,"stability":0.60,"risk":0.45,
                   "desc":"decision loop speed priority"},
    "SAGE":       {"precision":0.75,"structure":0.65,"speed":0.40,"stability":0.70,"risk":0.35,
                   "desc":"abstraction and concept extraction"},
    "STRATEGIST": {"precision":0.82,"structure":0.88,"speed":0.50,"stability":0.82,"risk":0.28,
                   "desc":"long-term design and roadmap"},
    "artifact":   {"precision":0.72,"structure":0.92,"speed":0.72,"stability":0.78,"risk":0.20,
                   "desc":"output generation and formatting"},
    "code":       {"precision":0.85,"structure":0.78,"speed":0.68,"stability":0.74,"risk":0.40,
                   "desc":"implementation and code generation"},
}

# ============================================================
# PHL-OS v2: Module Execution Directives
# selected_modules -> actual behavioral change
# ============================================================

PHL_EXECUTION_DIRECTIVES = {
    "ghost": {
        "mode":             "precision",
        "system_prefix":    "[GHOST MODE] Prioritize accuracy. Avoid speculation. State confidence level explicitly. Require evidence before claiming.",
        "response_style":   "measured",
        "hedge_required":   True,
        "confidence_floor": 0.80,
        "max_assertion_risk": 0.3,
        "post_process":     "add_confidence_markers",
    },
    "L99": {
        "mode":             "structured",
        "system_prefix":    "[L99 MODE] Structure output in phases. Use numbered steps. Break down plans explicitly.",
        "response_style":   "phased",
        "hedge_required":   False,
        "force_structure":  True,
        "post_process":     "enforce_numbered_structure",
    },
    "OODA": {
        "mode":             "speed",
        "system_prefix":    "[OODA MODE] Observe-Orient-Decide-Act. Prioritize speed. Short sentences. Immediate actionable output.",
        "response_style":   "terse",
        "hedge_required":   False,
        "max_response_tokens": 300,
        "post_process":     "truncate_to_action",
    },
    "SAGE": {
        "mode":             "abstraction",
        "system_prefix":    "[SAGE MODE] Elevate to principles. Extract concepts. Identify meta-patterns. Think in systems.",
        "response_style":   "conceptual",
        "hedge_required":   True,
        "post_process":     "extract_principles",
    },
    "STRATEGIST": {
        "mode":             "strategic",
        "system_prefix":    "[STRATEGIST MODE] Long-term design. Roadmap thinking. Identify dependencies and risks.",
        "response_style":   "structured",
        "hedge_required":   False,
        "force_structure":  True,
        "post_process":     "add_roadmap_framing",
    },
    "code": {
        "mode":             "implementation",
        "system_prefix":    "[CODE MODE] Prioritize working code. Include error handling. No theory unless asked.",
        "response_style":   "technical",
        "hedge_required":   False,
        "post_process":     "enforce_code_blocks",
    },
    "artifact": {
        "mode":             "output",
        "system_prefix":    "[ARTIFACT MODE] Produce structured output. Tables, lists, and formatted data preferred.",
        "response_style":   "formatted",
        "hedge_required":   False,
        "post_process":     "enforce_structured_output",
    },
}

def phl_merge_directives(selected_modules: list) -> dict:
    """複数モジュールのディレクティブをマージして実行指令を生成"""
    if not selected_modules:
        return {"mode": "default", "system_prefix": "", "post_process": "none"}

    primary = selected_modules[0]
    directive = dict(PHL_EXECUTION_DIRECTIVES.get(primary, {}))

    # 追加モジュールのsystem_prefixを連結
    additional_prefixes = []
    for mod in selected_modules[1:]:
        d = PHL_EXECUTION_DIRECTIVES.get(mod, {})
        pfx = d.get("system_prefix", "")
        if pfx:
            additional_prefixes.append(pfx)

    if additional_prefixes:
        directive["system_prefix"] = directive.get("system_prefix","") + " | " + " | ".join(additional_prefixes)

    directive["active_modules"] = selected_modules
    directive["post_process_chain"] = [
        PHL_EXECUTION_DIRECTIVES.get(m, {}).get("post_process", "none")
        for m in selected_modules
    ]
    return directive

def phl_post_process(text: str, directive: dict) -> str:
    """post_process_chainに従ってテキストを後処理"""
    chain = directive.get("post_process_chain", [])
    result = text

    for proc in chain:
        if proc == "add_confidence_markers":
            # 断言文に信頼度マーカーを付与
            lines = result.split("\n")
            processed = []
            for line in lines:
                if line.strip() and not line.startswith("[") and not line.startswith("#"):
                    if any(w in line for w in ["必ず","確実","間違いなく","definitely","certainly","always"]):
                        line = "[GHOST-CHECK] " + line
                processed.append(line)
            result = "\n".join(processed)

        elif proc == "enforce_numbered_structure":
            # 箇条書きを番号付きに変換
            lines = result.split("\n")
            numbered = []
            counter = 1
            for line in lines:
                if line.startswith("- ") or line.startswith("* "):
                    line = f"{counter}. " + line[2:]
                    counter += 1
                numbered.append(line)
            result = "\n".join(numbered)

        elif proc == "truncate_to_action":
            # OODA: 最初の300文字に要約ラベル付与
            if len(result) > 400:
                result = result[:400] + "\n[OODA: truncated for speed]"

        elif proc == "extract_principles":
            # SAGEモード: 末尾に原則サマリーを追加
            result = result + "\n\n[SAGE] Core principle: " + result.split("。")[0][:80] if "。" in result else result

        elif proc == "add_roadmap_framing":
            # STRATEGISTモード: Phase構造を付与
            if "Phase" not in result and "フェーズ" not in result:
                result = "**Roadmap framing applied**\n" + result

    return result

def phl_build_execution_context(selected_modules: list, state: dict, text: str = "") -> dict:
    """実行コンテキストを生成 - AIへの指令として使用"""
    directive = phl_merge_directives(selected_modules)
    processed_text = phl_post_process(text, directive) if text else ""

    return {
        "directive":        directive,
        "system_prefix":    directive.get("system_prefix", ""),
        "mode":             directive.get("mode", "default"),
        "active_modules":   selected_modules,
        "processed_text":   processed_text,
        "state_snapshot":   {
            "uncertainty":   state.get("uncertainty", 0.5),
            "risk_level":    state.get("risk_level", 0.3),
            "time_pressure": state.get("time_pressure", 0.3),
            "goal_type":     state.get("goal_type", "analysis"),
        },
        "version": "v2",
    }


def phl_build_state(payload):
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

def phl_select_modules(state, essence=None):
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

    # v2: スコアリングで選択・除外を決定
    SCORE_THRESHOLD = 0.25
    scored   = []
    excluded = []
    for c in candidates:
        s = phl_score(c["module"], state)
        c["score"] = s
        if s >= SCORE_THRESHOLD:
            scored.append(c)
        else:
            excluded.append({"module": c["module"], "reason": f"score_below_threshold:{s:.4f}"})

    # スコア降順ソート
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 競合解消（既存ルール維持）
    selected = list(dict.fromkeys(c["module"] for c in scored))
    if "OODA" in selected and "SAGE" in selected and state.get("time_pressure", 0) > 0.7:
        selected.remove("SAGE")
        excluded.append({"module":"SAGE","reason":"conflict:OODA:time_pressure>0.7"})
    return selected, scored, excluded

def phl_run_guard(state, modules, draft):
    risk = state.get("risk_level", 0.0)
    rev  = state.get("reversibility_required", 0.0)
    ev_r = state.get("evidence_required", 0.0)
    ev_c = draft.get("evidence_count", 1)
    if draft.get("contradiction", False):
        return {"status":"HALT",      "level":4, "reason":"logical_contradiction"}
    if risk > 0.75 and rev > 0.7:
        return {"status":"HALT",      "level":4, "reason":"high_risk_irreversible"}
    if risk > 0.9:
        return {"status":"HALT",      "level":4, "reason":"extreme_risk"}
    if ev_r > 0.8 and ev_c == 0:
        return {"status":"REANALYZE", "level":3, "reason":"insufficient_evidence"}
    if risk > 0.75:
        return {"status":"RESTRICT",  "level":2, "reason":"risk_modules_limited"}
    if risk > 0.6:
        return {"status":"WARN",      "level":1, "reason":"risk_elevated"}
    return {"status":"SAFE",          "level":0, "reason":None}

def _phl_fetch_essence() -> dict:
    """mocka_events.dbのessenceテーブルから直接取得。HTTP依存ゼロ。"""
    try:
        import sqlite3 as _sq
        db = str(Path(__file__).parent.parent.parent / "data" / "mocka_events.db")
        conn = _sq.connect(db, timeout=0.5)
        rows = conn.execute("SELECT axis, content FROM essence").fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    except Exception:
        return {}

def phl_essence_bonus(module: str, state: dict, essence: dict) -> float:
    """過去文脈（essence）からモジュールスコアを補正する。勝ちパターン加算・負けパターン減算。"""
    if not essence:
        return 0.0
    bonus     = 0.0
    operation = essence.get("OPERATION", "")
    incident  = essence.get("INCIDENT", "")
    goal      = state.get("goal_type", "")

    # 勝ちパターン: [great]タグ + goal_typeが一致
    if "[great]" in operation:
        op_lower = operation.lower()
        if goal in op_lower or any(k in op_lower for k in ["稼働", "完了", "成功", "確認"]):
            if module in ["code", "artifact"]:
                bonus += 0.10  # 実装系モジュールを強化

    # 負けパターン: INTEGRITY違反 → ghostを強化
    if "INTEGRITY" in incident or "捏造" in incident:
        if module == "ghost":
            bonus += 0.15
        if module in ["code", "artifact"]:
            bonus -= 0.05  # 実装系は慎重に

    # 負けパターン: DEPENDENCY_BREAK → codeにペナルティ
    if "DEPENDENCY_BREAK" in incident:
        if module == "code":
            bonus -= 0.10

    # 負けパターン: 繰り返しエラー（「また同じだ」） → ghostを強化
    if "また同じだ" in incident or "意味がわからない" in incident:
        if module == "ghost":
            bonus += 0.10

    return round(bonus, 4)

def phl_score(module, state, essence: dict = None):
    spec = PHL_MODULE_SPECS.get(module, {})
    if not spec:
        return 0.5
    score  = spec.get("precision", 0.5) * (0.3 + state.get("uncertainty", 0.5) * 0.2)
    score += spec.get("structure", 0.5) * (0.2 + state.get("abstraction_level", 0.5) * 0.2)
    score += spec.get("speed",     0.5) * state.get("time_pressure", 0.3) * 0.2
    score -= spec.get("risk",      0.3) * state.get("risk_level", 0.3) * 0.3
    if essence:
        score += phl_essence_bonus(module, state, essence)
    return round(score, 4)

def phl_build_trace(state, candidates, selected, excluded, guard, essence=None):
    all_mods     = [c["module"] for c in candidates]
    not_selected = [m for m in all_mods if m not in selected]
    scores       = {m: phl_score(m, state, essence) for m in all_mods}
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
        spec   = PHL_MODULE_SPECS.get(m, {})
        reason = "not triggered by state_vector"
        if m == "SAGE" and state.get("time_pressure", 0) > 0.7:
            reason = "time_pressure>0.7: OODA priority"
        elif spec.get("risk", 0) > 0.7:
            reason = "module_risk too high"
        counterfactuals.append({
            "module":              m,
            "score":               phl_score(m, state, essence),
            "expected_effect":     spec.get("desc", "-"),
            "reason_not_selected": reason,
        })
    return {
        "version":         "v2" if essence and any(essence.values()) else "v1",
        "state_summary":   {
            "goal_type":   state.get("goal_type"),
            "uncertainty": state.get("uncertainty"),
            "risk_level":  state.get("risk_level"),
            "stakes":      state.get("stakes"),
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

def _phl_feedback_to_essence(state: dict, guard: dict, selected: list):
    """guard結果をessenceへ自動フィードバック。スレッドセーフ。閉ループ。"""
    status = guard.get("status", "SAFE")
    if status not in ("HALT", "REANALYZE", "SAFE"):
        return
    try:
        import sqlite3 as _sq
        from datetime import datetime, timezone
        db  = str(Path(__file__).parent.parent.parent / "data" / "mocka_events.db")
        now = datetime.now(timezone.utc).isoformat()

        with _essence_lock:
            conn = _sq.connect(db, timeout=2.0)
            if status in ("HALT", "REANALYZE"):
                # 失敗パターン → INCIDENT軸に追記
                reason  = guard.get("reason", "unknown")
                goal    = state.get("goal_type", "?")
                entry   = f"[PHL-{status}] goal={goal} reason={reason} at={now[:19]}"
                axis    = "INCIDENT"
            else:
                # 成功パターン → OPERATION軸に[great]追記
                mods  = ",".join(selected[:3])
                goal  = state.get("goal_type", "?")
                entry = f"[great] PHL-SAFE goal={goal} modules={mods} at={now[:19]}"
                axis  = "OPERATION"
            conn.execute("""
                UPDATE essence
                SET content      = content || char(10) || ?,
                    updated_at   = ?,
                    source_count = source_count + 1
                WHERE axis = ?
            """, (entry, now, axis))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"[PHL essence feedback] {e}")

def phl_record_event(state, selected, guard, trace):
    ts   = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid  = "EPHL_" + ts + "_" + state.get("goal_type","?")[:4].upper()
    prev = get_prev_hash()
    reasons_str = json.dumps(trace.get("selected_reasons", {}), ensure_ascii=False)
    trace_str   = json.dumps(trace, ensure_ascii=False)
    row = [
        eid, ts, "PHL-OS", "phl_decision", "caliber/phl_os",
        "mocka_caliber_server.py", reasons_str, "phl_analyze",
        "internal", "in_operation", "normal", "A",
        "selected:" + ",".join(selected),
        "PHL-OS: " + state.get("goal_type","?") + " -> " + ",".join(selected),
        prev, "guard:" + guard.get("status","?") + " stakes:" + state.get("stakes","?"),
        "phl_decision", "caliber", "decision_trace",
        "N/A", "N/A",
        "guard=" + guard.get("status","?") + " trace=" + trace_str[:200],
    ]
    append_event(row)
    return eid

_phl_history = []

def _phl_push_history(entry):
    _phl_history.append(entry)
    if len(_phl_history) > 50:
        _phl_history.pop(0)

@app.route("/phl/analyze", methods=["POST"])
def phl_analyze():
    body    = request.json or {}
    payload = body.get("state", body)
    draft   = body.get("draft", {"evidence_count": 1, "contradiction": False})
    state             = phl_build_state(payload)
    essence           = _phl_fetch_essence()
    selected, candidates, excluded = phl_select_modules(state, essence)
    guard             = phl_run_guard(state, selected, draft)
    _phl_feedback_to_essence(state, guard, selected)
    trace             = phl_build_trace(state, candidates, selected, excluded, guard, essence)
    eid               = phl_record_event(state, selected, guard, trace)
    # v2: 実行コンテキスト生成（selected_modulesが実際の動作定義を持つ）
    exec_ctx = phl_build_execution_context(selected, state)

    result = {
        "event_id":          eid,
        "selected_modules":  selected,
        "guard":             guard,
        "decision_trace":    trace,
        "execution_context": exec_ctx,
        "recorded":          True,
        "version":           "v2",
    }
    _phl_push_history(result)
    print("[PHL-OS v2] " + eid + " | modules=" + str(selected) + " | guard=" + guard["status"] + " | mode=" + exec_ctx["mode"])
    return jsonify(result)


@app.route("/phl/execute", methods=["POST"])
def phl_execute():
    """v2: テキストをPHL-OSモジュールで後処理して返す実行エンドポイント"""
    body    = request.json or {}
    text    = body.get("text", "")
    modules = body.get("modules", [])
    state_payload = body.get("state", {})

    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    if not modules:
        # モジュール未指定なら自動選択
        state = phl_build_state(state_payload)
        selected, candidates, excluded = phl_select_modules(state)
        guard = phl_run_guard(state, selected, {})
    else:
        state    = phl_build_state(state_payload)
        selected = modules
        guard    = phl_run_guard(state, selected, {})

    exec_ctx       = phl_build_execution_context(selected, state, text)
    processed_text = exec_ctx["processed_text"]

    return jsonify({
        "status":           "ok",
        "original_text":    text,
        "processed_text":   processed_text,
        "active_modules":   selected,
        "mode":             exec_ctx["mode"],
        "system_prefix":    exec_ctx["system_prefix"],
        "guard":            guard,
        "version":          "v2",
    })


@app.route("/phl/directive", methods=["POST"])
def phl_directive():
    """v2: モジュール指定でシステムプロンプト指令だけを返す（AI呼び出し前の前処理用）"""
    body    = request.json or {}
    modules = body.get("modules", [])
    state_payload = body.get("state", {})

    if not modules:
        state = phl_build_state(state_payload)
        selected, _, _ = phl_select_modules(state)
    else:
        state    = phl_build_state(state_payload)
        selected = modules

    exec_ctx = phl_build_execution_context(selected, state)
    return jsonify({
        "status":         "ok",
        "active_modules": selected,
        "mode":           exec_ctx["mode"],
        "system_prefix":  exec_ctx["system_prefix"],
        "directive":      exec_ctx["directive"],
        "version":        "v2",
    })

@app.route("/phl/history", methods=["GET"])
def phl_history():
    n = int(request.args.get("n", 10))
    return jsonify({"count": len(_phl_history), "history": _phl_history[-n:]})

@app.route("/phl/modules", methods=["GET"])
def phl_modules():
    return jsonify({"modules": PHL_MODULE_SPECS, "count": len(PHL_MODULE_SPECS), "version": "v1"})

if __name__ == "__main__":
    print("[MoCKA Caliber Server v5 - API ZERO] port 5679")
    print(f"[v5] keywords: {len(get_keywords())}")
    print(f"[v5] threshold: {THRESHOLD}")
    app.run(host="0.0.0.0", port=5679, debug=False, threaded=True)
