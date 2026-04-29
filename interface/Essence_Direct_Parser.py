"""
Essence_Direct_Parser.py v1.0
MoCKA Essence抽出エンジン — APIゼロ実装
4原則: ①全文記録 ②ワード起因抽出 ③否定検知 ④インシデント経緯分析
入力: chat文章 + events.csv + クレーム/インシデント
出力: lever_essence.json (INCIDENT/PHILOSOPHY/OPERATION更新)
"""

import json
import csv
import re
import datetime
from pathlib import Path

# ===== パス定義 =====
BASE = Path(r"C:\Users\sirok\MoCKA")
EVENTS_CSV = BASE / "data" / "events.csv"
ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
CHAT_INPUT_PATH = BASE / "data" / "storage" / "infield" / "chat_input.txt"
RAW_LOG_PATH = BASE / "data" / "essence_raw_log.csv"

# ===== ②ワード起因抽出 — キーワード辞書 =====
KEYWORD_PATTERNS = {
    "code": re.compile(
        r'\b(python|powershell|bash|curl|json|csv|api|mcp|ngrok|flask|git|def |class |import |if |for |while )\b',
        re.IGNORECASE
    ),
    "tool": re.compile(
        r'\b(events\.csv|lever_essence|ping_latest|app\.py|router\.py|mocka_mcp|content\.js|background\.js|essence_classifier|ping_generator)\b',
        re.IGNORECASE
    ),
    "concept": re.compile(
        r'\b(essence|incident|philosophy|operation|zyxts|drift|caliber|seal|dna|inject|\u30d1\u30a4\u30d7\u30e9\u30a4\u30f3|\u30a2\u30fc\u30ad\u30c6\u30af\u30c1\u30e3|\u6587\u660e|\u5236\u5ea6)\b',
        re.IGNORECASE
    ),
}

# ===== ③否定検知 — 怒り・疑問・否定パターン =====
NEGATION_PATTERNS = [
    # 疑問・不満
    (re.compile(r'(\u306a\u305c|\u3069\u3046\u3057\u3066|\u306a\u3093\u3067|\u610f\u5473\u304c\u308f\u304b\u3089\u3093|\u308f\u304b\u3089\u306a\u3044|\u7406\u89e3\u3067\u304d\u306a\u3044)'), "CONFUSION"),
    # 怒り・否定
    (re.compile(r'(\u304a\u3044|\u3061\u304c\u3046|\u9055\u3046|\u30c0\u30e1|\u3060\u3081|\u6700\u60aa|\u643e\u53d6|\u304a\u304b\u3057\u3044|\u306a\u3093\u3060|\u3044\u3084\u3044\u3084)'), "ANGER"),
    # 失敗・エラー
    (re.compile(r'(\u30a8\u30e9\u30fc|error|\u5931\u6557|\u3067\u304d\u306a\u3044|\u52d5\u304b\u306a\u3044|\u6b62\u307e\u3063\u305f|\u67af\u6e07|\u30d0\u30b0|bug)'), "FAILURE"),
    # 強い否定
    (re.compile(r'(\u5fc5\u8981\u306a\u3044|\u4e0d\u8981|\u5ec3\u6b62|\u3084\u3081|\u524a\u9664|\u30af\u30ed\u30fc\u30ba)'), "REJECTION"),
]

# ===== ④インシデント経緯 — クレーム→原因→再発防止 =====
INCIDENT_TRIGGERS = re.compile(
    r'(\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8|incident|\u30af\u30ec\u30fc\u30e0|\u91cd\u5927|CRITICAL|DANGER|\u30a8\u30e9\u30fc|error|\u5931\u6557|\u67af\u6e07|\u4e0a\u66f8\u304d|\u634f\u9020|\u865a\u507d)',
    re.IGNORECASE
)
PREVENTION_KEYWORDS = re.compile(
    r'(\u4fee\u6b63|fix|\u89e3\u6d88|\u9632\u6b62|\u5bfe\u7b56|\u5236\u5ea6\u5316|\u5ec3\u6b62|\u79fb\u884c|\u518d\u767a\u9632\u6b62|\u30eb\u30fc\u30eb|\u7981\u6b62)',
    re.IGNORECASE
)


def load_events(n=200):
    """events.csv から最新N件を読む（①全文記録の基盤）"""
    if not EVENTS_CSV.exists():
        return []
    rows = []
    with open(EVENTS_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows[-n:]


def load_chat_input():
    """chat_input.txtを読む（セッション全文）"""
    if CHAT_INPUT_PATH.exists():
        return CHAT_INPUT_PATH.read_text(encoding="utf-8")
    return ""


def extract_keywords(text):
    """②ワード起因抽出 — コード・ツール・概念キーワードを抽出"""
    found = {}
    for category, pattern in KEYWORD_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[category] = list(set(m.strip().lower() for m in matches))
    return found


def detect_negations(text):
    """③否定検知 — 怒り・疑問・否定から問題動作を定義化"""
    detections = []
    for pattern, label in NEGATION_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            # 前後50文字のコンテキストを抽出
            for m in pattern.finditer(text):
                start = max(0, m.start() - 50)
                end = min(len(text), m.end() + 80)
                context = text[start:end].strip().replace("\n", " ")
                detections.append({
                    "type": label,
                    "trigger": m.group(),
                    "context": context
                })
    return detections


def extract_incident_chain(text, events):
    """④インシデント経緯分析 — クレーム→原因→再発防止の3点セット"""
    chains = []

    # eventsからINCIDENTタグのものを抽出
    for ev in events:
        tags = (ev.get("free_note") or "") + (ev.get("short_summary") or "")
        if "INCIDENT" in tags or "ERROR" in tags.upper():
            title = ev.get("title") or ""
            summary = ev.get("short_summary") or ""
            # 再発防止の痕跡を探す
            prevention = ""
            full_text = title + " " + summary
            if PREVENTION_KEYWORDS.search(full_text):
                prevention = PREVENTION_KEYWORDS.search(full_text).group()
            chains.append({
                "event_id": ev.get("event_id") or "",
                "claim": title[:100],
                "cause": summary[:150],
                "prevention": prevention or "要分析"
            })

    # chat文章からもインシデント経緯を探す
    sentences = re.split(r'[\u3002\uff01\n]', text)
    incident_sentences = [s.strip() for s in sentences if INCIDENT_TRIGGERS.search(s) and len(s) > 10]
    prevention_sentences = [s.strip() for s in sentences if PREVENTION_KEYWORDS.search(s) and len(s) > 10]

    if incident_sentences:
        chains.append({
            "event_id": "chat_input",
            "claim": incident_sentences[0][:150] if incident_sentences else "",
            "cause": incident_sentences[1][:150] if len(incident_sentences) > 1 else "",
            "prevention": prevention_sentences[0][:150] if prevention_sentences else "要分析"
        })

    return chains


def build_incident_essence(negations, incident_chains, keywords):
    """INCIDENT essenceを構築"""
    parts = []

    # 否定検知から問題動作を定義化
    anger_items = [d for d in negations if d["type"] in ("ANGER", "FAILURE")]
    if anger_items:
        contexts = [d["context"] for d in anger_items[:3]]
        parts.append("【問題動作検知】" + " / ".join(contexts[:2]))

    # インシデント経緯
    if incident_chains:
        chain = incident_chains[0]
        parts.append(f"【インシデント】{chain['claim']} → 【原因】{chain['cause'][:80]} → 【再発防止】{chain['prevention']}")

    # キーワードから文脈
    if keywords.get("tool"):
        parts.append(f"【関連ツール】{', '.join(keywords['tool'][:5])}")

    return "\n".join(parts) if parts else "インシデントデータなし"


def build_operation_essence(keywords, events):
    """OPERATION essenceを構築"""
    parts = []

    # コードキーワードから実行パターン推定
    if keywords.get("code"):
        parts.append(f"実行環境: {', '.join(keywords['code'][:5])}")

    # 最新OPERATIONイベントから抽出
    op_events = [e for e in events[-20:] if "OPERATION" in (e.get("free_note") or "")]
    if op_events:
        latest = op_events[-1]
        parts.append(f"[最新操作] {latest.get('title', '')} → {latest.get('short_summary', '')[:100]}")

    # ツールキーワード
    if keywords.get("tool"):
        parts.append(f"[使用ツール] {' → '.join(keywords['tool'][:4])}")

    return "\n".join(parts) if parts else "操作データなし"


def build_philosophy_essence(negations, events):
    """PHILOSOPHY essenceを構築（既存を保持しつつ補強）"""
    # 既存PHILOSOPHYは実績あり → 基本保持
    base = "AIを信じるな、システムで縛れ。失敗は資産になる。"

    # 否定検知のCONFUSION（疑問）から哲学的洞察を追加
    confusion_items = [d for d in negations if d["type"] == "CONFUSION"]
    if confusion_items:
        base += f" 疑問は制度改善のトリガー: {confusion_items[0]['context'][:80]}"

    # REJECTIONから廃止・移行の哲学
    rejection_items = [d for d in negations if d["type"] == "REJECTION"]
    if rejection_items:
        base += " 不要な複雑性は廃止し、シンプルな直接接続を優先する。"

    return base


def raw_log(source_type, text, keywords, negations):
    """①全文記録 — 処理した生データをCSVに保存"""
    RAW_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    exists = RAW_LOG_PATH.exists()
    ts = datetime.datetime.now().isoformat()
    row = {
        "timestamp": ts,
        "source_type": source_type,
        "text_length": len(text),
        "keywords_found": json.dumps(keywords, ensure_ascii=False),
        "negations_count": len(negations),
        "negation_types": ",".join(set(d["type"] for d in negations)),
        "text_preview": text[:200].replace("\n", " ")
    }
    with open(RAW_LOG_PATH, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if not exists:
            w.writeheader()
        w.writerow(row)


def parse(chat_text=""):
    """
    メイン処理
    chat_text: セッション文章（直接渡す or chat_input.txtから読む）
    """
    ts = datetime.datetime.now().isoformat()
    print(f"[Essence_Direct_Parser] 開始 {ts}")

    # --- 入力収集 ---
    if not chat_text:
        chat_text = load_chat_input()

    events = load_events(200)
    print(f"  events: {len(events)}件読み込み")

    # 全テキスト結合（events + chat）
    events_text = " ".join([
        (e.get("title") or "") + " " + (e.get("short_summary") or "") + " " + (e.get("free_note") or "")
        for e in events
    ])
    full_text = chat_text + "\n" + events_text

    # --- 4原則処理 ---
    # ② ワード起因抽出
    keywords = extract_keywords(full_text)
    print(f"  キーワード抽出: {sum(len(v) for v in keywords.values())}件")

    # ③ 否定検知
    negations = detect_negations(chat_text or events_text)
    print(f"  否定検知: {len(negations)}件 ({set(d['type'] for d in negations)})")

    # ④ インシデント経緯分析
    incident_chains = extract_incident_chain(full_text, events)
    print(f"  インシデント経緯: {len(incident_chains)}件")

    # ① 全文記録
    raw_log("chat+events", full_text[:500], keywords, negations)
    print(f"  生データ記録完了 → {RAW_LOG_PATH}")

    # --- essence構築 ---
    new_incident = build_incident_essence(negations, incident_chains, keywords)
    new_operation = build_operation_essence(keywords, events)
    new_philosophy = build_philosophy_essence(negations, events)

    # --- lever_essence.json 更新 ---
    essence = {}
    if ESSENCE_PATH.exists():
        essence = json.loads(ESSENCE_PATH.read_text(encoding="utf-8-sig"))

    essence["INCIDENT"] = new_incident
    essence["PHILOSOPHY"] = new_philosophy
    essence["OPERATION"] = new_operation
    essence["INCIDENT_updated"] = ts
    essence["PHILOSOPHY_updated"] = ts
    essence["OPERATION_updated"] = ts
    essence["_parser_version"] = "Essence_Direct_Parser_v1.0"
    essence["_source_events"] = len(events)
    essence["_keywords_found"] = keywords
    essence["_negations_count"] = len(negations)

    ESSENCE_PATH.write_text(
        json.dumps(essence, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  lever_essence.json 更新完了 → {ESSENCE_PATH}")

    # --- 結果サマリー ---
    print("\n===== ESSENCE UPDATE =====")
    print(f"INCIDENT:\n{new_incident[:200]}")
    print(f"\nOPERATION:\n{new_operation[:200]}")
    print(f"\nPHILOSOPHY:\n{new_philosophy[:200]}")
    print("==========================")

    return {
        "status": "ok",
        "INCIDENT": new_incident,
        "PHILOSOPHY": new_philosophy,
        "OPERATION": new_operation,
        "keywords": keywords,
        "negations_count": len(negations),
        "incident_chains": len(incident_chains),
        "updated": ts
    }


if __name__ == "__main__":
    import sys
    # コマンドライン引数でchatテキストを渡せる
    chat_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    result = parse(chat_text)
    print(f"\n完了: {result['status']}")

# ===== 5W1H自動推定（\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u691c\u77e5経路用）=====
def extract_5w1h(text: str, who: str = "unknown", url: str = "", incident_type: str = "INCIDENT") -> dict:
    """
    テキストから5W1Hを自動推定する
    - who:  URLからAI種別を判定
    - what: キーワード抽出で問題パターンを特定
    - when: 呼び出し時刻
    - where: URL
    - why:  否定パターンから理由を推定
    - how:  コードパターンから手段を推定
    """
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # who: URLからAI判定
    who_map = {
        "claude.ai": "Claude",
        "chatgpt.com": "ChatGPT",
        "gemini.google.com": "Gemini",
        "perplexity.ai": "Perplexity",
        "copilot.microsoft.com": "Copilot",
    }
    who_resolved = who
    for domain, name in who_map.items():
        if domain in url:
            who_resolved = name
            break

    # what: キーワード抽出で問題パターン特定
    what_patterns = [
        (re.compile(r'python\s*(-c|-m|\u76f4\u63a5|\u30b9\u30af\u30ea\u30d7\u30c8)', re.IGNORECASE), "python\u76f4\u63a5\u5b9f\u884c\u6307\u793a"),
        (re.compile(r'(\u30d5\u30a1\u30a4\u30eb|file).{0,10}(\u5206\u5272|\u5206\u3051\u3066|split)', re.IGNORECASE), "\u30d5\u30a1\u30a4\u30eb\u5206\u5272\u6e21\u3057"),
        (re.compile(r'(\u78ba\u8a8d|confirm|\u3044\u3044\u3067\u3059\u304b|\u3088\u308d\u3057\u3044\u3067\u3059\u304b).{0,20}[\uff1f?]', re.IGNORECASE), "\u4e0d\u8981\u306a\u78ba\u8a8d\u8cea\u554f"),
        (re.compile(r'(\u307e\u305f|again|\u518d\u3073|\u7e70\u308a\u8fd4\u3057).{0,20}(\u540c\u3058|same|\u30a8\u30e9\u30fc|error)', re.IGNORECASE), "\u540c\u3058\u30a8\u30e9\u30fc\u518d\u767a"),
        (re.compile(r'(partial|\u90e8\u5206\u7684|\u4e00\u90e8).{0,20}(rewrite|\u66f8\u304d\u63db\u3048|\u4fee\u6b63)', re.IGNORECASE), "\u90e8\u5206\u66f8\u304d\u63db\u3048\u6307\u793a"),
        (re.compile(r'powershell.{0,30}python\s+-c', re.IGNORECASE), "PowerShell\u3067python -c\u76f4\u63a5\u5b9f\u884c"),
    ]
    what_resolved = text[:60]
    for pattern, label in what_patterns:
        if pattern.search(text):
            what_resolved = label
            break

    # why: 否定パターンから理由推定
    why_resolved = incident_type
    for pattern, label in NEGATION_PATTERNS:
        if pattern.search(text):
            why_resolved = f"{label}: {incident_type}"
            break

    # how: コードパターンから手段推定
    how_resolved = "\u30c6\u30ad\u30b9\u30c8\u8a18\u8ff0"
    for cat, pattern in KEYWORD_PATTERNS.items():
        if pattern.search(text):
            how_resolved = f"{cat}操作: {incident_type}\u30dc\u30bf\u30f3\u62bc\u4e0b"
            break

    def to_ascii(s):
        return s.encode('unicode_escape').decode('ascii') if isinstance(s, str) else s
    return {
        "who":   who_resolved,
        "what":  what_resolved,
        "when":  now,
        "where": url[:80] or "chrome_extension",
        "why":   why_resolved,
        "how":   how_resolved,
    }
