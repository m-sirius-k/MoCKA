import json
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    from language_detector import LanguageDetector
    _detector = LanguageDetector()
    _has_detector = True
except Exception:
    _has_detector = False

ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")

PHILOSOPHY_KEYWORDS = [
    "失敗は資産", "再現性が信頼", "評価は軌跡", "哲学", "本質",
    "信じるな", "縛れ", "文明", "制度核", "信頼より証明", "A+B/2"
]
INCIDENT_KEYWORDS = [
    "インシデント", "エラー", "バグ", "障害", "再発",
    "INSTRUCTION_IGNORE", "暴走", "誤記録", "不一致", "失敗",
    "ミス", "崩壊", "クレーム", "INTEGRITY_VIOLATION"
]
CONFUSION_KEYWORDS = [
    "なぜ", "なんで", "どうして", "違う", "そうじゃない",
    "意味がわからない", "おかしい", "ちがう", "ずれている",
    "急に変えるな", "そんな指示はしていない", "また同じ",
    "前と違う", "返答がない", "通らない", "矛盾",
    "答えは", "説明は", "どこを読んだ", "何を根拠に",
    "最悪", "時間の無駄", "もういい", "ガッカリ",
    "動かない", "エラー", "失敗した", "通らない"
]
WHY_PATTERNS   = ["なぜなら", "目的は", "理由は", "ため", "目指す", "解決", "改善", "防止"]
HOW_PATTERNS   = ["実行", "修正", "追加", "実施", "スクリプト", "commit", "自動", "完了", "処理"]
WHO_PATTERNS   = ["Claude", "Gemini", "GPT", "Copilot", "きむら博士", "Perplexity"]
WHERE_PATTERNS = ["router.py", "events.csv", "MCP", "COMMAND CENTER", "caliber", "essence", "ledger"]

def extract_5w1h(text: str, source: str) -> dict:
    who = source
    for w in WHO_PATTERNS:
        if w in text:
            who = w
            break
    what  = text[:40].strip()
    when  = datetime.now().isoformat()
    where = "MoCKA_system"
    for w in WHERE_PATTERNS:
        if w in text:
            where = w
            break
    why = ""
    for w in WHY_PATTERNS:
        if w in text:
            idx = text.find(w)
            why = text[idx:idx+30].strip()
            break
    how = ""
    for w in HOW_PATTERNS:
        if w in text:
            idx = text.find(w)
            how = text[idx:idx+30].strip()
            break
    return {
        "who":   who,
        "what":  what,
        "when":  when,
        "where": where,
        "why":   why if why else "記録・制度化のため",
        "how":   how if how else "MoCKA自動記録",
    }

def classify(text: str) -> str:
    if _has_detector:
        detection = _detector.analyze(text)
        level = detection.get("level", "INFO")
        if level in ("DANGER", "CRITICAL"):
            return "INCIDENT"
        if level == "WARNING":
            for kw in INCIDENT_KEYWORDS:
                if kw in text:
                    return "INCIDENT"
    confusion_count = sum(1 for kw in CONFUSION_KEYWORDS if kw in text)
    if confusion_count >= 3:
        return "INCIDENT"
    for kw in PHILOSOPHY_KEYWORDS:
        if kw in text:
            return "PHILOSOPHY"
    for kw in INCIDENT_KEYWORDS:
        if kw in text:
            return "INCIDENT"
    return "OPERATION"

def analyze_danger(text: str) -> dict:
    if _has_detector:
        return _detector.analyze(text)
    return {"level": "INFO", "score": 0, "matched_words": [], "findings": {}}

def add_essence(text: str, source: str = "Claude") -> dict:
    """INCIDENT/PHILOSOPHY/OPERATION辞書構造に直接追記する"""
    if ESSENCE_PATH.exists():
        data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    else:
        data = {}

    # 構造保証: 3軸キーが必ず存在する
    for key in ("INCIDENT", "PHILOSOPHY", "OPERATION"):
        if key not in data:
            data[key] = ""

    essence_type = classify(text)
    now = datetime.now().isoformat()

    # 重複チェック
    existing = data.get(essence_type, "")
    if text[:60] in existing:
        return {"status": "SKIP", "reason": "duplicate"}

    # 既存テキストに追記（最新1000文字に制限）
    current = data.get(essence_type, "")
    combined = (current + "\n" + text).strip()
    data[essence_type] = combined[-1000:]
    data[f"{essence_type}_updated"] = now

    ESSENCE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    danger = analyze_danger(text)
    return {
        "status":       "ADDED",
        "type":         essence_type,
        "danger_level": danger.get("level", "INFO"),
        "danger_score": danger.get("score", 0),
    }

if __name__ == "__main__":
    tests = [
        ("Geminiが統計値Z=0.88を捏造した。INTEGRITY_VIOLATIONインシデント。", "Claude"),
        ("失敗は資産になる。経験に記録を重ねることが文明の基礎だ。", "きむら博士"),
        ("router.pyのDEPENDENCY_BREAKを修正。what_type=save誤記録を解消した。", "Claude"),
        ("なぜそうなるの？答えはさっきと違う。意味がわからない。また同じだ。", "きむら博士"),
    ]
    print("=== essence_classifier + language_detector 統合テスト ===\n")
    for text, source in tests:
        result = add_essence(text, source)
        print(f"入力: {text[:50]}")
        print(f"  -> status={result['status']} type={result.get('type')} danger={result.get('danger_level')}")
        print()