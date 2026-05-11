"""
MoCKA Guidelines Engine v2.1
events.db → 行動指針抽出エンジン
UTF-8 / ノイズフィルタ強化版
"""
import sqlite3, json, re, hashlib
from datetime import datetime, timezone
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DB_PATH    = MOCKA_ROOT / "data" / "mocka_events.db"
GUIDELINES = MOCKA_ROOT / "data" / "guidelines.json"
ESSENCE    = MOCKA_ROOT / "data" / "essence_condensed.json"
PROCESSED  = MOCKA_ROOT / "data" / "guidelines_processed.json"

# ===== ノイズパターン（強化版） =====
NOISE_PATTERNS = [
    r"^Mode\s+LastWriteTime",
    r"^FullName\s*$",
    r"^FullName\s*[-]+",
    r"^LineNumber",
    r"^Line\s+[-]+",
    r"^[-]+\s*$",
    r"^wt\s+-w\s+",
    r"^@app\.route",
    r"^async function",
    r"^const\s+\w+",
    r"_json\.dump\(",
    r"http://\w+\.py",
    r"^\s*OK:\s+\w+",
    r"^\s*NG:\s+",
    r"^done$",
    r"^DONE$",
    r"^FOUND:",
    r"^REPLACED:",
    r"^\s*\d+\s+\w+\s+\w+\s*$",
    r"^PS C:\\
",
    r"^StatusCode\s*:",
    r"background\.js:\d+",
    r"content\.js:\d+",
    r"^\d+$",
    r"^https?://",
    r"Access-Control-Allow-Origin",
    r"net::ERR_",
    r"Enumerating objects",
    r"Writing objects",
    r"document\.querySelector",
    r"^\{\"event_id\"",
    r"RawContent\s*:",
    r"Content-Type:",
    r"VM\d+:\d+",
    r"DIV font-sans",
    r"cloudflareaccess\.com",
    r"^N/A$",
    r"^Storage mission",
    r"^ingest_complete",
    # ファイルパスノイズ（強化）
    r"^[\"']*[A-Za-z]:\\",
    r"^\.\\"  ,
    r"\.(py|js|json|bat|exe|txt|csv|db)[\"'\s]*$",
    r"mocka.extension.background",
    r"mocka.extension.content",
    r"MoCKA.tools.",
    # PowerShellノイズ
    r"^Copy-Item",
    r"^Invoke-",
    r"CategoryInfo",
    r"FullyQualifiedErrorId",
    r"発生場所 行",
    # gitノイズ
    r"Delta compression",
    r"Compressing objects",
    r"remote: Resolving",
    r"pack-reused",
]

# ===== 思想シグナル（日本語） =====
THOUGHT_SIGNALS = [
    r"なぜ|どうして|なんで|どうやって",
    r"これって|どういう|おかしい",
    r"重要|優先|本質|核心",
    r"こうしよう|やろう|変更|修正",
    r"違う|ちがう|そうじゃない|そこはない",
    r"わかった|気づ|なるほど",
    r"そうか|そういうこと",
    r"いいね|グレート|ヒント|うまい",
    r"ダメ|おかしい|また|再発",
    r"設計|制度|方針|ルール|定義",
    r"mocka|MoCKA|caliber|essence|PHL|SPP",
    r"確認|調べて|数えて",
    r"進捗|完了|確定",
    r"面倒|難易|大事|重要|本題",
]

# ===== インシデントキーワード =====
INCIDENT_KW = {
    "INCIDENT":  ["インシデント", "エラー", "失敗", "障害", "バグ",
                  "壊れ", "動かない", "文字化け", "UTF", "CRITICAL",
                  "WARNING", "error", "Error"],
    "MATAKA":    ["またか", "また同じ", "再発", "繰り返", "何度も"],
    "DECISION":  ["決定", "承認", "採用", "方針", "確定",
                  "これで行く", "こうする"],
    "INSIGHT":   ["わかった", "気づ", "なるほど", "ヒント", "グレート"],
    "CHALLENGE": ["違う", "そうじゃない", "おかしい", "ダメ", "そこはない"],
}

NOISE_RE  = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]
SIGNAL_RE = [re.compile(p, re.IGNORECASE) for p in THOUGHT_SIGNALS]


# ===== 品質チェック =====
def is_noise(t: str) -> bool:
    if not t or len(t.strip()) < 8:
        return True
    t = t.strip()
    if any(p.search(t) for p in NOISE_RE):
        return True
    # 制御文字混入
    if sum(1 for ch in t if ord(ch) < 0x20 and ch not in "\t\n\r") >= 1:
        return True
    # 半角カタカナ = 文字化けの証拠
    if sum(1 for ch in t if 0xFF61 <= ord(ch) <= 0xFF9F) >= 1:
        return True
    # ファイルパスのみ（意味なし）
    cleaned = re.sub(r'"[A-Za-z]:\\[^"]*"', "", t).strip()
    cleaned = re.sub(r"'[A-Za-z]:\\[^']*'", "", cleaned).strip()
    if len(cleaned) < 5:
        return True
    # 意味ある文字が最低必要
    japanese = re.findall(r'[\u3040-\u9FFF\u30A0-\u30FF\u4E00-\u9FFF]', t)
    ascii_words = re.findall(r'[A-Za-z]{3,}', t)
    if len(japanese) < 3 and len(ascii_words) < 2:
        return True
    return False


def classify(t: str) -> str:
    for cat, kws in INCIDENT_KW.items():
        if any(k in t for k in kws):
            return cat
    return "GENERAL"


def score_text(t: str, risk: str = "") -> float:
    if is_noise(t):
        return 0.0
    s = min(sum(1 for p in SIGNAL_RE if p.search(t)) * 0.15, 0.6)
    l = len(t)
    s += 0.2 if 10 <= l <= 200 else (0.1 if l <= 500 else 0)
    cat = classify(t)
    s += 0.3 if cat in ("INCIDENT", "MATAKA") else \
         (0.2 if cat in ("DECISION", "INSIGHT", "CHALLENGE") else 0)
    if risk in ("WARNING", "CRITICAL", "DANGER"):
        s += 0.2
    return min(s, 1.0)


# ===== DBからイベント取得 =====
def fetch_events(db_path: Path, limit: int = 2000):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, when_ts, who_actor, what_type,
               where_component, why_purpose, how_trigger,
               risk_level, title, short_summary, free_note
        FROM events
        WHERE what_type IN (
               'user_voice','save','record','collaboration','share',
               'incident','ai_violation','governance_degradation',
               'environment_error','data_quality','config_error',
               'security','cli','ingest','mataka','claim','decision'
           )
           OR risk_level IN ('WARNING','CRITICAL','DANGER','high')
           OR what_type LIKE '%incident%'
           OR what_type LIKE '%violation%'
        ORDER BY when_ts DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ===== 処理済みID管理 =====
def load_processed(path: Path):
    if path.exists():
        return set(json.loads(path.read_text(encoding="utf-8")).get("processed_ids", []))
    return set()


def save_processed(path: Path, ids):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "processed_ids": list(ids),
        "updated": datetime.now(timezone.utc).isoformat()
    }, ensure_ascii=False, indent=2), encoding="utf-8")


# ===== 5W1H抽出 =====
def extract_5w1h(text: str, ev: dict) -> dict:
    cat = classify(text)
    who = ev.get("who_actor") or "kimura"
    if "Claude" in text: who = "Claude"
    elif "Gemini" in text: who = "Gemini"
    what_map = {
        "INCIDENT": "インシデント発生",
        "MATAKA":   "再発",
        "DECISION": "意思決定・確定",
        "INSIGHT":  "気づき",
        "CHALLENGE":"課題",
        "GENERAL":  "記録",
    }
    when = str(ev.get("when_ts") or "")[:10]
    why  = "不明"
    for pattern in [r"なぜ(.{0,50})[。．\n]", r"原因は(.{0,50})[。．\n]"]:
        m = re.search(pattern, text)
        if m:
            why = m.group(1).strip()
            break
    # source_textからパス文字列を除去
    clean_text = re.sub(r'"[A-Za-z]:\\[^"]*"', "", text).strip()
    clean_text = re.sub(r'\s+', " ", clean_text)[:200]
    return {
        "who":         who,
        "what":        what_map.get(cat, "記録"),
        "when":        when,
        "where":       ev.get("where_component") or "claude.ai",
        "why":         why,
        "how":         ev.get("how_trigger") or "chrome_extension",
        "category":    cat,
        "source_text": clean_text,
    }


# ===== 再発防止アクション生成 =====
def generate_prevention(w5h1: dict) -> dict:
    cat = w5h1["category"]
    how_map = {
        "INCIDENT":  "prevention_queueに登録 → Human Gate承認 → essence INCIDENT軸に記録",
        "MATAKA":    "danger_patterns.jsonに追加 → 自動検知強化 → COMMAND CENTER警告",
        "DECISION":  "guidelines.jsonに追加 → PHL注入で次セッションから有効",
        "INSIGHT":   "guidelines.jsonに追加 → essence PHILOSOPHY更新",
        "CHALLENGE": "action_guidelineとして登録 → セッション開始時に展開",
        "GENERAL":   "guidelines.jsonに追加して参照可能に維持",
    }
    return {
        "who":   "Claude + きむら博士",
        "what":  f"{cat}への対処",
        "when":  "次回同一状況で",
        "where": "MoCKAシステム全体",
        "why":   f"{w5h1['why']}の再発防止",
        "how":   how_map.get(cat, ""),
    }


# ===== ガイドラインデータ管理 =====
def load_guidelines(path: Path) -> dict:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if "summary" not in data:
            data["summary"] = {"total": 0, "by_category": {}, "last_updated": ""}
        return data
    return {
        "meta": {
            "version": "2.0",
            "philosophy": "失敗は資産になる",
            "created": datetime.now(timezone.utc).isoformat(),
        },
        "guidelines": [],
        "summary": {"total": 0, "by_category": {}, "last_updated": ""},
    }


def save_guidelines(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    cats = {}
    for g in data["guidelines"]:
        cat = g.get("category", "GENERAL")
        cats[cat] = cats.get(cat, 0) + 1
    data["summary"].update({
        "total":        len(data["guidelines"]),
        "by_category":  cats,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    })
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_guideline(data: dict, w5h1: dict, prevention: dict,
                  eid: str, score: float) -> bool:
    fp = hashlib.md5(
        f"{w5h1['category']}:{w5h1['source_text'][:80]}".encode()
    ).hexdigest()[:12]
    if any(g.get("fingerprint") == fp for g in data["guidelines"]):
        return False
    cat       = w5h1["category"]
    directive = f"【{cat}】{w5h1['source_text'][:70]}… → {prevention['how']}"
    data["guidelines"].append({
        "id":               f"GL_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{fp}",
        "fingerprint":      fp,
        "category":         cat,
        "score":            round(score, 3),
        "source_event_id":  eid,
        "created":          datetime.now(timezone.utc).isoformat(),
        "trust_score":      score,
        "cause_5w1h":       w5h1,
        "prevention_5w1h":  prevention,
        "action_directive": directive,
    })
    return True


# ===== essence注入 =====
def inject_to_essence(essence_path: Path, guidelines_data: dict):
    if not essence_path.exists():
        print(f"[WARN] essence not found: {essence_path}")
        return
    essence = json.loads(essence_path.read_text(encoding="utf-8"))
    top5 = sorted(
        guidelines_data["guidelines"],
        key=lambda g: g.get("score", 0), reverse=True
    )[:5]
    if not top5:
        return
    now   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [l for l in essence.get("PHILOSOPHY", "").split("\n")
             if not l.startswith("[GL:")]
    lines.append(f"[{now}] Guidelines Engine v2.1 TOP5:")
    for g in top5:
        lines.append(f"[GL:{g['category']}] {g['action_directive'][:100]}")
    phil_key = next(
        (k for k in ["PHILOSOPHY", "philosophy"] if k in essence),
        "PHILOSOPHY"
    )
    essence[phil_key] = "\n".join(lines[-20:])
    essence_path.write_text(
        json.dumps(essence, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[OK] essence PHILOSOPHY: {len(top5)}件注入")


# ===== メイン =====
def run(score_threshold: float = 0.50, max_new: int = 500):
    print("=" * 60)
    print("MoCKA Guidelines Engine v2.1")
    print("=" * 60)
    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}")
        return
    processed = load_processed(PROCESSED)
    print(f"[INFO] 処理済み: {len(processed)}件")
    events = fetch_events(DB_PATH)
    print(f"[INFO] 取得: {len(events)}件")
    gdata = load_guidelines(GUIDELINES)
    print(f"[INFO] 既存ガイドライン: {len(gdata['guidelines'])}件")

    new_c = skip_n = skip_l = skip_d = 0
    for ev in events:
        if new_c >= max_new:
            break
        eid = ev.get("event_id", "")
        if eid in processed:
            skip_d += 1
            continue
        text = (
            ev.get("title") or
            ev.get("free_note") or
            ev.get("short_summary") or ""
        ).strip()
        if not text:
            processed.add(eid)
            continue
        if is_noise(text):
            skip_n += 1
            processed.add(eid)
            continue
        score = score_text(text, ev.get("risk_level", ""))
        if score < score_threshold:
            skip_l += 1
            processed.add(eid)
            continue
        w5h1 = extract_5w1h(text, ev)
        prev = generate_prevention(w5h1)
        if add_guideline(gdata, w5h1, prev, eid, score):
            new_c += 1
            print(f"  [+] {w5h1['category']:10s} {score:.2f} | {text[:55]}…")
        processed.add(eid)

    save_guidelines(GUIDELINES, gdata)
    save_processed(PROCESSED, processed)
    inject_to_essence(ESSENCE, gdata)

    print()
    print("=" * 60)
    print(f"  新規: {new_c}件 | ノイズ除外: {skip_n}件 | 低スコア: {skip_l}件 | 処理済: {skip_d}件")
    print(f"  総ガイドライン数: {len(gdata['guidelines'])}件")
    for cat, cnt in gdata["summary"]["by_category"].items():
        print(f"    {cat:12s}: {cnt}件")
    print("=" * 60)


if __name__ == "__main__":
    run()
