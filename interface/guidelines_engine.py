"""
MoCKA Guidelines Engine v1.1
events.db実スキーマ対応版
"""
import sqlite3, json, re, hashlib
from datetime import datetime, timezone
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DB_PATH    = MOCKA_ROOT / "data" / "events.db"
GUIDELINES = MOCKA_ROOT / "data" / "guidelines.json"
ESSENCE    = MOCKA_ROOT / "data" / "lever_essence.json"
PROCESSED  = MOCKA_ROOT / "data" / "guidelines_processed.json"

NOISE_PATTERNS = [
    r"^PS C:\\\\", r"^StatusCode\s*:", r"background\.js:\d+",
    r"^\d+$", r"^https?://", r"Access-Control-Allow-Origin",
    r"net::ERR_", r"Enumerating objects", r"Writing objects",
    r"document\.querySelector", r"^\{\"event_id\"",
    r"RawContent\s*:", r"Content-Type:", r"VM\d+:\d+",
    r"DIV font-sans", r"cloudflareaccess\.com",
    r"^N/A$", r"^Storage mission", r"^ingest_complete",
]
THOUGHT_SIGNALS = [
    r"なぜ|どうして|なんで|どうやって", r"これって|どう思|どう考",
    r"問題|課題|懸念|疑問", r"こうしよう|やろう|改善|変更|修正",
    r"違う|ちがう|そうじゃない|そこはない",
    r"わかった|気づ|発見|なるほど", r"そうか|そういうこと",
    r"いいね|グレート|ヒント|うまい", r"ダメ|だめ|おかしい|間違",
    r"また|再発|繰り返|何度も", r"設計|構想|思想|方針|指針",
    r"mocka|MoCKA|caliber|essence|PHL|SPP",
    r"確認|見て|調べて|教えて", r"決定|採択|承認|確定",
    r"面白|重要|大事|核心|本質",
]
INCIDENT_KW = {
    "INCIDENT":  ["インシデント","エラー","失敗","問題","バグ","壊れ","動かない","文字化け","UTF","CRITICAL","WARNING","error"],
    "MATAKA":    ["またか","また同じ","再発","繰り返","何度も"],
    "DECISION":  ["決定","採択","承認","方針","確定","これで行く","こうする"],
    "INSIGHT":   ["わかった","気づ","発見","なるほど","ヒント","グレート"],
    "CHALLENGE": ["違う","そうじゃない","おかしい","ダメ","なぜ","そこはない"],
}

NOISE_RE  = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]
SIGNAL_RE = [re.compile(p, re.IGNORECASE) for p in THOUGHT_SIGNALS]

def is_noise(t):
    if not t or len(t.strip()) < 4: return True
    return any(p.search(t) for p in NOISE_RE)

def classify(t):
    for cat, kws in INCIDENT_KW.items():
        if any(k in t for k in kws): return cat
    return "GENERAL"

def score_text(t, risk=""):
    if is_noise(t): return 0.0
    s = min(sum(1 for p in SIGNAL_RE if p.search(t)) * 0.15, 0.6)
    l = len(t)
    s += 0.2 if 10<=l<=200 else (0.1 if l<=500 else 0)
    cat = classify(t)
    s += 0.3 if cat in ("INCIDENT","MATAKA") else (0.2 if cat in ("DECISION","INSIGHT","CHALLENGE") else 0)
    if risk in ("WARNING","CRITICAL","DANGER"): s += 0.2
    return min(s, 1.0)

def fetch_events(db_path, limit=2000):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, [when], who_actor, what_type,
               where_component, why_purpose, how_trigger,
               risk_level, title, short_summary, free_note
        FROM events
        WHERE what_type IN ('user_voice','incident','mataka','claim','record','decision')
           OR risk_level IN ('WARNING','CRITICAL','DANGER')
        ORDER BY [when] DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def load_processed(path):
    if path.exists():
        return set(json.loads(path.read_text(encoding="utf-8")).get("processed_ids", []))
    return set()

def save_processed(path, ids):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"processed_ids": list(ids),
        "updated": datetime.now(timezone.utc).isoformat()},
        ensure_ascii=False, indent=2), encoding="utf-8")

def extract_5w1h(text, ev):
    cat = classify(text)
    who = ev.get("who_actor") or "kimura"
    if "Claude" in text: who = "Claude"
    elif "Gemini" in text: who = "Gemini"
    what_map = {"INCIDENT":"問題発生","MATAKA":"再発","DECISION":"判断確定",
                "INSIGHT":"気づき","CHALLENGE":"異議","GENERAL":"記録"}
    when = str(ev.get("when") or "")[:10]
    why = "不明"
    for p in [r"なぜ(.{0,50})[？?。\n]", r"問題は(.{0,50})[。\n]"]:
        m = re.search(p, text)
        if m: why = m.group(1).strip(); break
    return {"who":who,"what":what_map.get(cat,"記録"),"when":when,
            "where":ev.get("where_component") or "claude.ai",
            "why":why,"how":ev.get("how_trigger") or "manual",
            "category":cat,"source_text":text[:200]}

def generate_prevention(w5h1):
    cat = w5h1["category"]
    how_map = {
        "INCIDENT": "prevention_queueに登録→Human Gate承認→essence INCIDENT軸に記録",
        "MATAKA":   "danger_patterns.jsonに追記→自動検知強化→COMMAND CENTER警告",
        "DECISION": "guidelines.jsonにAND追加→PHL注入で次セッションから有効",
        "INSIGHT":  "guidelines.jsonに追記→essence PHILOSOPHY更新",
        "CHALLENGE":"action_guidelineとして登録→セッション開始時に参照",
        "GENERAL":  "AND追記して参照可能に維持",
    }
    return {"who":"Claude+きむら博士","what":f"{cat}への対処",
            "when":"次回同一状況で","where":"MoCKAシステム全体",
            "why":f"{w5h1['why']}の再発防止","how":how_map.get(cat,"")}

def load_guidelines(path):
    if path.exists(): return json.loads(path.read_text(encoding="utf-8"))
    return {"meta":{"version":"1.1","philosophy":"失敗は資産になる",
                    "created":datetime.now(timezone.utc).isoformat()},
            "guidelines":[],"summary":{"total":0,"by_category":{},"last_updated":""}}

def save_guidelines(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    cats = {}
    for g in data["guidelines"]: cats[g.get("category","GENERAL")] = cats.get(g.get("category","GENERAL"),0)+1
    data["summary"].update({"total":len(data["guidelines"]),"by_category":cats,
                            "last_updated":datetime.now(timezone.utc).isoformat()})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_guideline(data, w5h1, prevention, eid, score):
    fp = hashlib.md5(f"{w5h1['category']}:{w5h1['source_text'][:80]}".encode()).hexdigest()[:12]
    if any(g.get("fingerprint")==fp for g in data["guidelines"]): return False
    cat = w5h1["category"]
    directive = f"【{cat}】{w5h1['source_text'][:70]}… → {prevention['how']}"
    data["guidelines"].append({
        "id": f"GL_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{fp}",
        "fingerprint":fp,"category":cat,"score":round(score,3),
        "source_event_id":eid,"created":datetime.now(timezone.utc).isoformat(),
        "trust_score":score,"cause_5w1h":w5h1,
        "prevention_5w1h":prevention,"action_directive":directive,
    })
    return True

def inject_to_essence(essence_path, guidelines_data):
    if not essence_path.exists(): print(f"[WARN] essence not found"); return
    essence = json.loads(essence_path.read_text(encoding="utf-8"))
    top5 = sorted(guidelines_data["guidelines"], key=lambda g:g.get("score",0), reverse=True)[:5]
    if not top5: return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [l for l in essence.get("PHILOSOPHY","").split("\n") if not l.startswith("[GL:")]
    lines.append(f"[{now}] Guidelines Engine v1.1 TOP5:")
    for g in top5: lines.append(f"[GL:{g['category']}] {g['action_directive'][:100]}")
    essence["PHILOSOPHY"] = "\n".join(lines[-20:])
    essence_path.write_text(json.dumps(essence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] essence PHILOSOPHY: {len(top5)}件注入")

def run(score_threshold=0.35, max_new=500):
    print("="*60)
    print("MoCKA Guidelines Engine v1.1")
    print("="*60)
    if not DB_PATH.exists(): print(f"[ERROR] DB not found: {DB_PATH}"); return
    processed = load_processed(PROCESSED)
    print(f"[INFO] 処理済み: {len(processed)}件")
    events = fetch_events(DB_PATH)
    print(f"[INFO] 取得: {len(events)}件")
    gdata = load_guidelines(GUIDELINES)
    print(f"[INFO] 既存指針: {len(gdata['guidelines'])}件")
    new_c=skip_n=skip_l=skip_d=0
    for ev in events:
        if new_c >= max_new: break
        eid = ev.get("event_id","")
        if eid in processed: skip_d+=1; continue
        text = (ev.get("title") or ev.get("free_note") or ev.get("short_summary") or "").strip()
        if not text: processed.add(eid); continue
        if is_noise(text): skip_n+=1; processed.add(eid); continue
        score = score_text(text, ev.get("risk_level",""))
        if score < score_threshold: skip_l+=1; processed.add(eid); continue
        w5h1 = extract_5w1h(text, ev)
        prev = generate_prevention(w5h1)
        if add_guideline(gdata, w5h1, prev, eid, score):
            new_c+=1
            print(f"  [+] {w5h1['category']:10s} {score:.2f} | {text[:55]}…")
        processed.add(eid)
    save_guidelines(GUIDELINES, gdata)
    save_processed(PROCESSED, processed)
    inject_to_essence(ESSENCE, gdata)
    print()
    print("="*60)
    print(f"  新規: {new_c}件 | ノイズ除外: {skip_n}件 | 低スコア: {skip_l}件 | 重複: {skip_d}件")
    print(f"  合計行動指針: {len(gdata['guidelines'])}件")
    for cat,cnt in gdata["summary"]["by_category"].items():
        print(f"    {cat:12s}: {cnt}件")
    print("="*60)

if __name__ == "__main__":
    run()
