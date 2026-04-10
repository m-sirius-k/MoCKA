import json
import re
from pathlib import Path
from datetime import datetime

ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")

PHILOSOPHY_KEYWORDS = [
    "地道", "失敗は資産", "実測が証明", "文明の基礎", "継承",
    "しなやか", "復元力", "景色", "本質", "哲学", "思想",
    "再現性", "信頼より構造", "縛る", "遊動座標", "A+B/2"
]
INCIDENT_KEYWORDS = [
    "インシデント", "エラー", "バグ", "捏造", "違反",
    "INSTRUCTION_IGNORE", "再発", "誤検知", "不整合", "嘘",
    "ミス", "断絶", "クレーム", "INTEGRITY_VIOLATION"
]

# 5W1H抽出キーワードマップ
WHY_PATTERNS = ["なぜなら", "目的は", "理由は", "ため", "目指す", "解決", "改善", "防止"]
HOW_PATTERNS = ["実装", "修正", "追加", "実行", "スクリプト", "commit", "自動", "経由", "処理"]
WHO_PATTERNS  = ["Claude", "Gemini", "GPT", "Copilot", "きむら博士", "Perplexity"]
WHERE_PATTERNS= ["router.py", "events.csv", "MCP", "COMMAND CENTER", "caliber", "essence", "ledger"]

def extract_5w1h(text: str, source: str) -> dict:
    """テキストから5W1Hを自動抽出"""
    # Who
    who = source
    for w in WHO_PATTERNS:
        if w in text:
            who = w
            break

    # What（先頭40文字を要約代わりに）
    what = text[:40].strip()

    # When
    when = datetime.now().isoformat()

    # Where
    where = "MoCKA_system"
    for w in WHERE_PATTERNS:
        if w in text:
            where = w
            break

    # Why
    why = ""
    for w in WHY_PATTERNS:
        if w in text:
            idx = text.find(w)
            why = text[idx:idx+30].strip()
            break

    # How
    how = ""
    for w in HOW_PATTERNS:
        if w in text:
            idx = text.find(w)
            how = text[idx:idx+30].strip()
            break

    return {
        "who": who,
        "what": what,
        "when": when,
        "where": where,
        "why": why if why else "記録・継承のため",
        "how": how if how else "MoCKA自動分類"
    }

def classify(text: str) -> str:
    for kw in PHILOSOPHY_KEYWORDS:
        if kw in text:
            return "PHILOSOPHY"
    for kw in INCIDENT_KEYWORDS:
        if kw in text:
            return "INCIDENT"
    return "OPERATION"

def add_essence(text: str, source: str = "Claude") -> dict:
    if ESSENCE_PATH.exists():
        data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    else:
        data = {"source": "auto_classified", "total_before_filter": 0,
                "filtered_count": 0, "essence": []}

    existing = [
        e if isinstance(e, str) else e.get("text", "")
        for e in data["essence"]
    ]
    if text in existing:
        return {"status": "SKIP", "reason": "duplicate"}

    essence_type = classify(text)
    w5h1 = extract_5w1h(text, source)

    entry = {
        "text": text,
        "type": essence_type,
        "source": source,
        "timestamp": w5h1["when"],
        "5w1h": w5h1
    }

    data["essence"].append(entry)
    data["filtered_count"] = len(data["essence"])
    ESSENCE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return {"status": "ADDED", "type": essence_type, "5w1h": w5h1}

if __name__ == "__main__":
    tests = [
        ("Geminiが固定値Z=0.88を捏造した。INTEGRITY_VIOLATIONインシデント。", "Claude"),
        ("失敗は資産になる。地道に記録し続けることが文明の基礎だ。", "きむら博士"),
        ("router.pyのDEPENDENCY_BREAKを修正。what_type=save誤記録を解消。", "Claude"),
    ]
    for text, source in tests:
        result = add_essence(text, source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
