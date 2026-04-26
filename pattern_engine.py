import json, os, requests
from datetime import datetime
from collections import Counter

MECAB_URL = "http://127.0.0.1:5003/parse"
BASE_DIR = "C:/Users/sirok/MoCKA/data"
SUCCESS_DB = BASE_DIR + "/success_patterns.json"
FAILURE_DB = BASE_DIR + "/failure_patterns.json"
PATTERN_SCORE = BASE_DIR + "/pattern_scores.json"

TARGET_POS = ["名詞", "動詞", "形容詞"]

# 除外するsurface（助詞・助動詞・記号のゴミ）
STOP_WORDS = set([
    "た","し","する","ある","ない","いる","なる","れる","られる",
    "て","で","に","を","は","が","の","と","も","や","か","へ",
    "から","まで","より","など","って","じゃ","けど","ので","ため",
    "こと","もの","これ","それ","あれ","ここ","そこ","あそこ",
    "。","、","・","「","」","（","）","…","—","*"
])

FAILURE_SIGNALS = [
    "エラー","失敗","できない","なぜ","なんで","おかしい",
    "違う","だめ","ダメ","問題","不具合","壊れ","停止",
    "error","Error","ERROR","false","None","null","死","落ち"
]

SUCCESS_SIGNALS = [
    "完了","成功","できた","よし","OK","ok","動いた","正常",
    "完璧","グレイト","ヒント","解決","確認","動作","稼働",
    "復旧","修正","達成","実現","起動","接続"
]

def tokenize(text):
    try:
        res = requests.post(MECAB_URL, json={"text": text}, timeout=5)
        return res.json().get("tokens", [])
    except Exception as e:
        print(f"[PATTERN] MeCab error: {e}")
        return []

def extract_keywords(tokens):
    keywords = []
    for t in tokens:
        if t.get("pos") not in TARGET_POS:
            continue
        surface = t.get("surface", "")
        base = t.get("base", "")
        if surface and surface not in STOP_WORDS and len(surface) > 1:
            keywords.append(surface)
        if base and base not in STOP_WORDS and base != surface and len(base) > 1:
            keywords.append(base)
    return keywords

def score_text(text):
    tokens = tokenize(text)
    keywords = extract_keywords(tokens)
    success_score = 0.0
    failure_score = 0.0
    matched_success = []
    matched_failure = []

    for kw in keywords:
        if kw in SUCCESS_SIGNALS:
            success_score += 2.0
            matched_success.append(kw)
        if kw in FAILURE_SIGNALS:
            failure_score += 2.0
            matched_failure.append(kw)

    if os.path.exists(SUCCESS_DB):
        with open(SUCCESS_DB, encoding="utf-8") as f:
            sdb = json.load(f)
        for entry in sdb.get("hint", []) + sdb.get("great", []):
            past_kw = set(extract_keywords(tokenize(entry.get("text", ""))))
            overlap = set(keywords) & past_kw - STOP_WORDS
            if overlap:
                success_score += len(overlap) * 0.5
                matched_success.extend(list(overlap))

    if os.path.exists(FAILURE_DB):
        with open(FAILURE_DB, encoding="utf-8") as f:
            fdb = json.load(f)
        for entry in fdb.get("claim", []) + fdb.get("incident", []):
            past_kw = set(extract_keywords(tokenize(entry.get("text", ""))))
            overlap = set(keywords) & past_kw - STOP_WORDS
            if overlap:
                failure_score += len(overlap) * 0.5
                matched_failure.extend(list(overlap))

    if failure_score > success_score * 1.5:
        verdict = "DANGER"
    elif failure_score > success_score:
        verdict = "WARNING"
    elif success_score > failure_score * 1.5:
        verdict = "SUCCESS"
    elif success_score > 0:
        verdict = "GOOD"
    else:
        verdict = "NEUTRAL"

    return {
        "success_score": round(success_score, 2),
        "failure_score": round(failure_score, 2),
        "verdict": verdict,
        "matched_success": list(set(matched_success)),
        "matched_failure": list(set(matched_failure)),
        "keywords": keywords[:20]
    }

def analyze_batch(texts):
    results = [score_text(t) for t in texts]
    verdicts = [r["verdict"] for r in results]
    counter = Counter(verdicts)
    danger_count = counter.get("DANGER", 0) + counter.get("WARNING", 0)
    success_count = counter.get("SUCCESS", 0) + counter.get("GOOD", 0)
    trend = "失敗傾向" if danger_count > success_count else "成功傾向" if success_count > danger_count else "中立"
    all_kw = []
    for r in results:
        all_kw.extend(r["keywords"])
    top_kw = [kw for kw, _ in Counter(all_kw).most_common(10)]
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "batch_size": len(texts),
        "trend": trend,
        "verdicts": dict(counter),
        "top_keywords": top_kw,
        "danger_ratio": round(danger_count / len(texts), 2) if texts else 0,
        "success_ratio": round(success_count / len(texts), 2) if texts else 0,
    }
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(PATTERN_SCORE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[PATTERN] batch完了: {trend} / danger:{danger_count} success:{success_count}")
    print(f"[PATTERN] top keywords: {top_kw}")
    return summary

if __name__ == "__main__":
    tests = [
        "AIを信じるな、システムで縛れ。失敗は資産になる。",
        "エラーが出た。なぜ動かない。また失敗した。",
        "完了！動いた！完璧です。グレイト！",
        "問題が発生した。不具合を確認。修正できない。",
        "解決した。正常に動作している。確認完了。"
    ]
    print("=== Pattern Engine v1.1 テスト ===")
    for t in tests:
        result = score_text(t)
        print(f"\n入力: {t[:30]}")
        print(f"  verdict : {result['verdict']}")
        print(f"  success : {result['success_score']} / failure: {result['failure_score']}")
        print(f"  keywords: {result['keywords']}")
    print("\n=== バッチ分析 ===")
    summary = analyze_batch(tests)
    print(json.dumps(summary, ensure_ascii=False, indent=2))