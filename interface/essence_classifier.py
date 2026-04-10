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

    # 重複チェック（textキーで比較）
    existing = [
        e if isinstance(e, str) else e.get("text", "")
        for e in data["essence"]
    ]
    if text in existing:
        return {"status": "SKIP", "reason": "duplicate"}

    essence_type = classify(text)
    entry = {
        "text": text,
        "type": essence_type,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }

    data["essence"].append(entry)
    data["filtered_count"] = len(data["essence"])

    ESSENCE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return {"status": "ADDED", "type": essence_type, "text": text[:40]}

if __name__ == "__main__":
    tests = [
        ("Geminiが固定値Z=0.88を捏造した。INTEGRITY_VIOLATIONインシデント。", "Claude"),
        ("失敗は資産になる。地道に記録し続けることが文明の基礎だ。", "きむら博士"),
        ("router.pyのDEPENDENCY_BREAKを修正。what_type='save'誤記録を解消。", "Claude"),
    ]
    for text, source in tests:
        result = add_essence(text, source)
        print(result)
