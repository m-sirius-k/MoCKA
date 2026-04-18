import json
import re
import sys
from pathlib import Path
from datetime import datetime

# LanguageDetectorをインポート（同一ディレクトリ）
sys.path.insert(0, str(Path(__file__).parent))
try:
    from language_detector import LanguageDetector
    _detector = LanguageDetector()
    _has_detector = True
except Exception:
    _has_detector = False

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

# ============================================================
# 否定文・誤解検知キーワード（Language Algorithm v1.0）
# ============================================================
CONFUSION_KEYWORDS = [
    "なぜ", "なんで", "どうして", "違う", "そうじゃない",
    "意味がわからん", "おかしい", "ちがう", "ズレている",
    "勝手に変えるな", "そんな指示はしていない", "また同じ",
    "前と違う", "論点が違う", "筋が通らない", "矛盾",
    "根拠は", "証拠は", "どこを読んだ", "何を根拠に",
    "最悪", "時間の無駄", "もういい", "ガッカリ",
    "動かない", "エラー", "失敗した", "通らない"
]

# 5W1H抽出キーワードマップ
WHY_PATTERNS   = ["なぜなら", "目的は", "理由は", "ため", "目指す", "解決", "改善", "防止"]
HOW_PATTERNS   = ["実装", "修正", "追加", "実行", "スクリプト", "commit", "自動", "経由", "処理"]
WHO_PATTERNS   = ["Claude", "Gemini", "GPT", "Copilot", "きむら博士", "Perplexity"]
WHERE_PATTERNS = ["router.py", "events.csv", "MCP", "COMMAND CENTER", "caliber", "essence", "ledger"]


def extract_5w1h(text: str, source: str) -> dict:
    """テキストから5W1Hを自動抽出"""
    who = source
    for w in WHO_PATTERNS:
        if w in text:
            who = w
            break

    what = text[:40].strip()
    when = datetime.now().isoformat()

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
        "why":   why  if why  else "記録・継承のため",
        "how":   how  if how  else "MoCKA自動分類"
    }


def classify(text: str) -> str:
    """
    テキストをPHILOSOPHY / INCIDENT / CONFUSION / OPERATIONに分類。
    優先順位: CONFUSION > INCIDENT > PHILOSOPHY > OPERATION
    """
    # 言語アルゴリズム: 否定文・危険信号を最優先でINSIDENT化
    if _has_detector:
        detection = _detector.analyze(text)
        level = detection.get("level", "INFO")
        if level in ("DANGER", "CRITICAL"):
            return "INCIDENT"
        if level == "WARNING":
            # WARNING + 既存INCIDENTキーワードがあればINCIDENT確定
            for kw in INCIDENT_KEYWORDS:
                if kw in text:
                    return "INCIDENT"

    # 否定文キーワード単独チェック（detector未使用の場合のフォールバック）
    confusion_count = sum(1 for kw in CONFUSION_KEYWORDS if kw in text)
    if confusion_count >= 3:
        return "INCIDENT"

    # 通常分類
    for kw in PHILOSOPHY_KEYWORDS:
        if kw in text:
            return "PHILOSOPHY"
    for kw in INCIDENT_KEYWORDS:
        if kw in text:
            return "INCIDENT"

    return "OPERATION"


def analyze_danger(text: str) -> dict:
    """テキストの危険度を返す（Language Algorithm v1.0）"""
    if _has_detector:
        return _detector.analyze(text)
    return {"level": "INFO", "score": 0, "matched_words": [], "findings": {}}


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
    danger = analyze_danger(text)

    entry = {
        "text":         text,
        "type":         essence_type,
        "source":       source,
        "timestamp":    w5h1["when"],
        "5w1h":         w5h1,
        "danger_level": danger.get("level", "INFO"),
        "danger_score": danger.get("score", 0),
        "danger_words": danger.get("matched_words", []),
    }

    data["essence"].append(entry)
    data["filtered_count"] = len(data["essence"])
    ESSENCE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return {
        "status":       "ADDED",
        "type":         essence_type,
        "5w1h":         w5h1,
        "danger_level": danger.get("level", "INFO"),
        "danger_score": danger.get("score", 0),
    }


if __name__ == "__main__":
    tests = [
        ("Geminiが固定値Z=0.88を捏造した。INTEGRITY_VIOLATIONインシデント。", "Claude"),
        ("失敗は資産になる。地道に記録し続けることが文明の基礎だ。", "きむら博士"),
        ("router.pyのDEPENDENCY_BREAKを修正。what_type=save誤記録を解消。", "Claude"),
        ("なぜそうなる？根拠は？さっきと言ってることが違う。動かない。また同じ。", "きむら博士"),
        ("勝手に変えるな。そんな指示はしていない。最悪。時間の無駄。", "きむら博士"),
    ]
    print("=== essence_classifier + language_detector 統合テスト ===\n")
    for text, source in tests:
        result = add_essence(text, source)
        print(f"入力: {text[:50]}")
        print(f"  -> type={result['status']=='ADDED' and result.get('type')} "
              f"danger={result.get('danger_level')} score={result.get('danger_score')}")
        print()
