"""
MoCKA Language Detector v2 — 危険信号予測エンジン
ハインリッヒの法則 1:29:300 ドライブレコーダー理論

v2変更点:
  - ストップワード除外（日本語助詞・一般語・MoCKA技術用語）
  - 文字化けフィルタ追加
  - Tier1語彙の精査（技術記録語を除外）

実行:
  python language_detector.py analyze   # events.csv全件分析・自動学習
  python language_detector.py scan TEXT # テキストをリアルタイム判定
  python language_detector.py report    # 統計レポート出力
"""

import sys
import json
import csv
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE           = Path("C:/Users/sirok/MoCKA")
EVENTS_CSV     = BASE / "data/events.csv"
PATTERNS_JSON  = BASE / "interface/danger_patterns.json"
REPORT_PATH    = BASE / "data/danger_report.json"

INCIDENT_LEVELS   = {"INCIDENT", "CRITICAL", "ERROR"}
INCIDENT_KEYWORDS = ["インシデント", "クレーム", "データ消失", "上書き", "INCIDENT", "CRITICAL"]
LOOKBACK_WINDOW   = 30

# ── ストップワード ────────────────────────────────────────

STOPWORDS = set([
    # 日本語一般語・助詞・語尾
    "これは","これが","これを","これで","これに","これら","これらの",
    "ます","です","した","して","する","ある","いる","なる","れる",
    "られる","ている","ました","ません","します","できる","行う",
    "この","その","あの","どの","ここ","そこ","あそこ",
    "から","まで","より","など","また","さらに","および",
    "ため","こと","もの","ところ","場合","とき","うえ",
    "について","による","として","において","に対して",
    "それぞれ","一方","なお","ただし","以下","上記","前述",
    "概要","詳細","説明","記録","保存","確認","完了",
    "実装","設計","構築","追加","更新","修正","変更",
    "削除","生成","作成","取得","処理","実行","起動",
    # MoCKA技術用語
    "MoCKA","mocka","Claude","claude","Gemini","gemini",
    "GPT","gpt","Perplexity","Copilot","essence","ESSENCE",
    "TODO","events","csv","planningcaliber","workshop",
    "caliber","CALIBER","intent","queue","Firestore","Firebase",
    "Python","python","PowerShell","powershell","router","app",
    "MCP","mcp","ngrok","localhost","interface","json","JSON",
    "commit","git","seal","Phase","phase",
    # IT一般
    "API","URL","HTTP","GET","POST","True","False","None",
    "null","true","false","import","from","def","class","return",
    # 文書語
    "このテキスト","システム全体","文明ループの","の文明ループ",
    "これらの洞察",
])

def is_valid_token(token: str) -> bool:
    if token in STOPWORDS:
        return False
    if len(token) < 2:
        return False
    # 文字化け除外
    if re.search(r'[^\u0000-\u007F\u3000-\u9FFF\uFF00-\uFFEF]', token):
        return False
    if token.startswith("_"):
        return False
    return True


# ── ユーティリティ ───────────────────────────────────────

def load_patterns() -> dict:
    with open(PATTERNS_JSON, encoding="utf-8") as f:
        return json.load(f)

def save_patterns(patterns: dict):
    patterns["stats"]["last_analyzed"] = datetime.now().isoformat()
    with open(PATTERNS_JSON, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

def load_events() -> list:
    events = []
    if not EVENTS_CSV.exists():
        return events
    with open(EVENTS_CSV, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append({k: (v or "").strip() for k, v in row.items()})
    return events

def extract_text(event: dict) -> str:
    fields = ["title","short_summary","description","free_note",
              "why_purpose","how_trigger","impact_result"]
    return " ".join(event.get(f,"") for f in fields)

def is_incident(event: dict, patterns: dict) -> bool:
    risk = event.get("risk_level","")
    if risk in INCIDENT_LEVELS:
        return True
    text = extract_text(event)
    for kw in patterns.get("incident_keywords", INCIDENT_KEYWORDS):
        if kw in text:
            return True
    return False

def tokenize(text: str) -> list:
    tokens  = re.findall(r'[a-zA-Z][a-zA-Z0-9]+', text)
    tokens += re.findall(r'[\u3040-\u9fff]{2,8}', text)
    return [t for t in tokens if is_valid_token(t)]


# ── スコアリング ─────────────────────────────────────────

def score_text(text: str, patterns: dict) -> dict:
    hits = {"Tier1":[],"Tier2":[],"Tier3":[]}

    t1 = patterns["patterns"]["Tier1"]["words"] + patterns["patterns"]["Tier1"].get("auto_learned",[])
    for w in t1:
        if w in text:
            hits["Tier1"].append(w)

    t2 = patterns["patterns"]["Tier2"]["words"] + patterns["patterns"]["Tier2"].get("auto_learned",[])
    t2_hits = [w for w in t2 if w in text]
    if len(t2_hits) >= patterns["patterns"]["Tier2"]["min_count"]:
        hits["Tier2"].extend(t2_hits)
    for combo in patterns["patterns"]["Tier2"]["combinations"]:
        if all(w in text for w in combo):
            hits["Tier2"].extend(combo)

    t3 = patterns["patterns"]["Tier3"]["words"] + patterns["patterns"]["Tier3"].get("auto_learned",[])
    for w in t3:
        if w in text:
            hits["Tier3"].append(w)

    if hits["Tier1"]:
        level, score = "CRITICAL", 100
    elif hits["Tier2"]:
        level = "DANGER"
        score = 60 + min(len(hits["Tier2"]) * 5, 35)
    elif hits["Tier3"]:
        level = "WARNING"
        score = 20 + min(len(hits["Tier3"]) * 5, 35)
    else:
        level, score = "INFO", 0

    return {
        "level": level,
        "score": score,
        "triggers": {k: list(set(v)) for k, v in hits.items()},
        "total_hits": sum(len(v) for v in hits.values())
    }


# ── 自動学習 ─────────────────────────────────────────────

def analyze_events(events: list, patterns: dict) -> dict:
    print(f"=== Language Detector v2: events.csv分析 ===")
    print(f"対象: {len(events)}件\n")

    incident_indices = [i for i,ev in enumerate(events) if is_incident(ev, patterns)]
    print(f"インシデント検知: {len(incident_indices)}件")

    if not incident_indices:
        print("インシデントイベントが見つかりませんでした。")
        return patterns

    pre_tokens, normal_tokens = [], []
    incident_set = set(incident_indices)

    for i, ev in enumerate(events):
        if i in incident_set:
            continue
        tokens = tokenize(extract_text(ev))
        is_pre = any(0 < (idx - i) <= LOOKBACK_WINDOW for idx in incident_indices)
        (pre_tokens if is_pre else normal_tokens).extend(tokens)

    pre_counter    = Counter(pre_tokens)
    normal_counter = Counter(normal_tokens)
    total_pre      = max(len(pre_tokens), 1)
    total_normal   = max(len(normal_tokens), 1)

    existing = set(
        patterns["patterns"]["Tier1"]["words"] +
        patterns["patterns"]["Tier2"]["words"] +
        patterns["patterns"]["Tier3"]["words"] +
        patterns["patterns"]["Tier1"].get("auto_learned",[]) +
        patterns["patterns"]["Tier2"].get("auto_learned",[]) +
        patterns["patterns"]["Tier3"].get("auto_learned",[])
    )

    new_t2, new_t3 = [], []
    for word, pre_count in pre_counter.most_common(300):
        if word in existing:
            continue
        pre_rate    = pre_count / total_pre
        normal_rate = normal_counter.get(word, 0) / total_normal
        ratio       = pre_rate / max(normal_rate, 0.0001)
        if ratio >= 5.0 and pre_count >= 5:
            new_t2.append((word, pre_count, round(ratio,1)))
        elif ratio >= 3.0 and pre_count >= 3:
            new_t3.append((word, pre_count, round(ratio,1)))

    added_t2 = [w for w,_,_ in new_t2[:20]]
    added_t3 = [w for w,_,_ in new_t3[:30]]

    patterns["patterns"]["Tier2"]["auto_learned"] = list(set(added_t2))
    patterns["patterns"]["Tier3"]["auto_learned"] = list(set(added_t3))
    patterns["stats"]["auto_learned_count"] = len(added_t2) + len(added_t3)
    patterns["stats"]["events_analyzed"]    = len(events)

    print(f"\n自動学習結果（ストップワード除外済み）:")
    print(f"  Tier2追加: {len(added_t2)}件")
    for w,c,r in new_t2[:20]:
        print(f"    [{w}] 出現{c}回 比率{r}倍")
    print(f"  Tier3追加: {len(added_t3)}件")
    for w,c,r in new_t3[:10]:
        print(f"    [{w}] 出現{c}回 比率{r}倍")

    return patterns


# ── レポート生成 ─────────────────────────────────────────

def generate_report(events: list, patterns: dict):
    print("\n=== 危険度レポート生成 ===")
    level_counts = Counter()
    danger_events = []

    for ev in events:
        result = score_text(extract_text(ev), patterns)
        level_counts[result["level"]] += 1
        if result["level"] in ("CRITICAL","DANGER","WARNING"):
            danger_events.append({
                "event_id": ev.get("event_id",""),
                "when":     ev.get("when",""),
                "title":    ev.get("title","")[:60],
                "level":    result["level"],
                "score":    result["score"],
                "triggers": result["triggers"]
            })

    c = level_counts["CRITICAL"]
    d = level_counts["DANGER"]
    w = level_counts["WARNING"]

    report = {
        "generated_at":       datetime.now().isoformat(),
        "total_events":       len(events),
        "level_distribution": dict(level_counts),
        "heinrich_ratio": {
            "CRITICAL":     c,
            "DANGER":       d,
            "WARNING":      w,
            "INFO":         level_counts["INFO"],
            "actual_ratio": f"1:{round(d/max(c,1),1)}:{round(w/max(c,1),1)}",
            "theory":       "1:29:300"
        },
        "danger_events": sorted(danger_events, key=lambda x: x["score"], reverse=True)[:50]
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  CRITICAL: {c}件")
    print(f"  DANGER:   {d}件")
    print(f"  WARNING:  {w}件")
    print(f"  INFO:     {level_counts['INFO']}件")
    print(f"  実測ハインリッヒ比: 1:{round(d/max(c,1),1)}:{round(w/max(c,1),1)}")
    print(f"  理論値:             1:29:300")
    print(f"\nレポート保存: {REPORT_PATH}")


# ── エントリーポイント ───────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    if cmd == "analyze":
        events   = load_events()
        patterns = load_patterns()
        patterns = analyze_events(events, patterns)
        save_patterns(patterns)
        generate_report(events, patterns)
        print("\n✅ 分析完了")
    elif cmd == "scan":
        text     = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        patterns = load_patterns()
        result   = score_text(text, patterns)
        print(f"\n判定: [{result['level']}] スコア={result['score']}")
        for tier, words in result["triggers"].items():
            if words:
                icon = {"Tier1":"🔴","Tier2":"🟠","Tier3":"🟡"}.get(tier,"")
                print(f"  {icon} {tier}: {words}")
    elif cmd == "report":
        events   = load_events()
        patterns = load_patterns()
        generate_report(events, patterns)
    else:
        print("使い方: python language_detector.py [analyze|scan TEXT|report]")
